import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

from apps.core.models import Notification
from apps.order.models import Order

logger = logging.getLogger(__name__)


SEAT_LOCK_TTL = 900
ORDER_EXPIRE_MINUTES = 30
SEAT_COLS = ['A', 'B', 'C', 'D', 'E', 'F']


def seat_lock_key(flight_id, seat_number):
    return f'seat_lock:{flight_id}:{seat_number}'


def lock_seat(flight_id, seat_number, user_id):
    key = seat_lock_key(flight_id, seat_number)
    existing = cache.get(key)
    if existing and existing != user_id:
        return False
    cache.set(key, user_id, SEAT_LOCK_TTL)
    return True


def release_seat_lock(flight_id, seat_number):
    cache.delete(seat_lock_key(flight_id, seat_number))


def get_seat_map(flight):
    rows = max(flight.total_seats // len(SEAT_COLS), 1)
    occupied = set(
        Order.objects.filter(
            flight=flight,
            status__in=['pending', 'paid', 'ticketed'],
            seat_number__isnull=False,
        ).exclude(seat_number='').values_list('seat_number', flat=True)
    )
    seats = []
    for row in range(1, rows + 1):
        for col in SEAT_COLS:
            number = f'{row}{col}'
            status = 'occupied' if number in occupied else 'available'
            lock_owner = cache.get(seat_lock_key(flight.id, number))
            if status == 'available' and lock_owner:
                status = 'locked'
            seats.append({
                'seat_number': number,
                'row': row,
                'col': col,
                'status': status,
            })
    return seats


def expire_pending_orders():
    now = timezone.now()
    expired = Order.objects.filter(status='pending', expires_at__lt=now)
    count = 0
    for order in expired:
        if order.cancel():
            count += 1
            create_notification(
                order.user,
                '订单已超时取消',
                f'订单 {order.order_id} 已超过支付时限，已自动取消。',
                'order',
                order.order_id,
            )
    return count


def try_fulfill_waitlist(flight):
    """座位释放后尝试为候补用户自动创建待支付订单"""
    from django.db import transaction
    from apps.order.services import create_single_order
    from apps.core.models import WaitlistEntry

    with transaction.atomic():
        flight.refresh_from_db()
        if not flight.is_available:
            return None

        entry = (
            WaitlistEntry.objects.select_for_update()
            .filter(flight=flight, status='waiting')
            .order_by('created_at')
            .first()
        )
        if not entry:
            return None

        try:
            order = create_single_order(entry.user, flight, {
                'passenger_name': entry.passenger_name,
                'passenger_id_card': entry.passenger_id_card,
                'cabin_class': entry.cabin_class,
                'seat_number': '',
            })
            entry.status = 'fulfilled'
            entry.order = order
            entry.save(update_fields=['status', 'order'])
            create_notification(
                entry.user,
                '候补购票成功 🎉',
                f'您候补的航班 {flight.flight_no}（{flight.departure_city}→{flight.arrival_city}）已有票源，'
                f'已为您生成订单 {order.order_id}，请在 30 分钟内完成支付。',
                'order',
                order.order_id,
            )
            return order
        except Exception:
            return None


def create_notification(user, title, content, notification_type='system', related_id='', notify_channels=True):
    notification = Notification.objects.create(
        user=user,
        title=title,
        content=content,
        notification_type=notification_type,
        related_id=related_id,
    )
    if notify_channels:
        _send_email_notification(user, title, content)
        _send_sms_notification(user, title, content)
    return notification


def _send_email_notification(user, title, content):
    email = getattr(user, 'email', None)
    if not email:
        return
    try:
        send_mail(
            subject=f'【机票预约平台】{title}',
            message=content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@flightbooking.local'),
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        logger.exception('邮件通知发送失败')


def _send_sms_notification(user, title, content):
    phone = getattr(user, 'phone', None)
    if not phone:
        return
    logger.info('[短信模拟] 发送至 %s: %s - %s', phone, title, content[:80])


def check_flight_alerts(flight):
    if flight.status in ['delayed', 'cancelled']:
        for alert in flight.alerts.filter(is_active=True):
            status_text = '延误' if flight.status == 'delayed' else '取消'
            create_notification(
                alert.user,
                f'航班{status_text}提醒',
                f'您关注的航班 {flight.flight_no}（{flight.departure_city}→{flight.arrival_city}）已{status_text}。',
                'flight',
                flight.flight_no,
            )
