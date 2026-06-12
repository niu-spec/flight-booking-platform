from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.core.services import create_notification, lock_seat, release_seat_lock
from apps.order.models import BookingGroup, Coupon, Order, UserCoupon


CABIN_MULTIPLIER = {
    'economy': Decimal('1.0'),
    'business': Decimal('1.5'),
    'first': Decimal('2.5'),
}
DELAY_INSURANCE_FEE = Decimal('25.00')


def calc_base_amount(flight, cabin_class):
    return flight.base_price * CABIN_MULTIPLIER.get(cabin_class, Decimal('1.0'))


def apply_coupon(user, coupon_code, amount):
    if not coupon_code:
        return Decimal('0'), None
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        raise serializers.ValidationError({'coupon_code': '优惠券不存在'})
    if not coupon.is_valid():
        raise serializers.ValidationError({'coupon_code': '优惠券已失效'})
    user_coupon = UserCoupon.objects.filter(user=user, coupon=coupon, is_used=False).first()
    if not user_coupon:
        raise serializers.ValidationError({'coupon_code': '您尚未领取该优惠券'})
    discount = coupon.calc_discount(amount)
    if discount <= 0:
        raise serializers.ValidationError({'coupon_code': '未达到优惠券使用门槛'})
    return discount, user_coupon


def validate_seat(flight, seat_number, user_id):
    if not seat_number:
        return
    from apps.core.services import get_seat_map
    seat_map = {s['seat_number']: s['status'] for s in get_seat_map(flight)}
    status = seat_map.get(seat_number)
    if status != 'available':
        raise serializers.ValidationError({'seat_number': '座位不可选'})
    if not lock_seat(flight.id, seat_number, user_id):
        raise serializers.ValidationError({'seat_number': '座位已被锁定'})


@transaction.atomic
def create_single_order(user, flight, data, booking_group=None, trip_leg='outbound'):
    cabin_class = data.get('cabin_class', 'economy')
    seat_number = data.get('seat_number') or ''

    if not flight.is_available:
        raise serializers.ValidationError({'flight': '该航班暂无可预订座位'})

    validate_seat(flight, seat_number, user.id)

    base_amount = calc_base_amount(flight, cabin_class)
    discount, user_coupon = apply_coupon(user, data.get('coupon_code'), base_amount)
    insurance_amount = DELAY_INSURANCE_FEE if data.get('delay_insurance') else Decimal('0')
    total_amount = base_amount - discount + insurance_amount

    if not flight.book_seats(1):
        if seat_number:
            release_seat_lock(flight.id, seat_number)
        raise serializers.ValidationError({'flight': '预订座位失败'})

    order = Order.objects.create(
        order_id=Order.generate_order_id(),
        total_amount=total_amount,
        discount_amount=discount,
        insurance_amount=insurance_amount,
        user=user,
        flight=flight,
        cabin_class=cabin_class,
        seat_number=seat_number or None,
        passenger_name=data['passenger_name'],
        passenger_id_card=data['passenger_id_card'],
        status='pending',
        booking_group=booking_group,
        trip_leg=trip_leg,
    )
    order.set_expiry()
    order.save(update_fields=['expires_at'])

    if user_coupon:
        user_coupon.is_used = True
        user_coupon.used_at = timezone.now()
        user_coupon.save(update_fields=['is_used', 'used_at'])
        user_coupon.coupon.used_count += 1
        user_coupon.coupon.save(update_fields=['used_count'])

    create_notification(
        user,
        '订单创建成功',
        f'订单 {order.order_id} 已创建，请在 30 分钟内完成支付。',
        'order',
        order.order_id,
    )
    return order


@transaction.atomic
def create_round_trip_orders(user, outbound_flight, return_flight, data):
    group = BookingGroup.objects.create(user=user, trip_type='round_trip')
    outbound_data = {**data, 'coupon_code': data.get('coupon_code')}
    outbound = create_single_order(user, outbound_flight, outbound_data, group, 'outbound')
    return_data = {
        'cabin_class': data.get('return_cabin_class', data.get('cabin_class', 'economy')),
        'seat_number': data.get('return_seat_number', ''),
        'passenger_name': data['passenger_name'],
        'passenger_id_card': data['passenger_id_card'],
        'delay_insurance': data.get('return_delay_insurance', False),
    }
    return_order = create_single_order(user, return_flight, return_data, group, 'return')
    return group, outbound, return_order


@transaction.atomic
def create_multi_leg_orders(user, flights, data, trip_type='transfer'):
    """中转/多程联程预订"""
    group = BookingGroup.objects.create(user=user, trip_type=trip_type)
    orders = []
    for i, flight in enumerate(flights):
        leg_data = {
            'cabin_class': data.get('cabin_class', 'economy'),
            'seat_number': (data.get('seat_numbers') or [''])[i] if i < len(data.get('seat_numbers') or []) else '',
            'passenger_name': data['passenger_name'],
            'passenger_id_card': data['passenger_id_card'],
            'delay_insurance': bool((data.get('delay_insurance_legs') or [False])[i]) if i < len(data.get('delay_insurance_legs') or []) else False,
        }
        if i == 0:
            leg_data['coupon_code'] = data.get('coupon_code', '')
        orders.append(create_single_order(user, flight, leg_data, group, f'segment_{i + 1}'))
    return group, orders
