from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import FlightAlert, Notification, WaitlistEntry
from apps.core.serializers import FlightAlertSerializer, NotificationSerializer, WaitlistEntrySerializer
from apps.core.services import expire_pending_orders
from apps.flight.models import Flight
from apps.order.models import Order
from apps.payment.models import Payment
from apps.user.models import CustomUser


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            n = Notification.objects.get(id=notification_id, user=request.user)
            n.is_read = True
            n.save(update_fields=['is_read'])
            return Response({'message': '已标记为已读'})
        except Notification.DoesNotExist:
            return Response({'error': '消息不存在'}, status=404)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': '全部已读'})


class FlightAlertListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FlightAlertSerializer

    def get_queryset(self):
        return FlightAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WaitlistListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WaitlistEntrySerializer

    def get_queryset(self):
        return WaitlistEntry.objects.filter(user=self.request.user).select_related('flight', 'order')

    def perform_create(self, serializer):
        entry = serializer.save()
        from apps.core.services import create_notification
        create_notification(
            self.request.user,
            '候补登记成功',
            f'您已加入 {entry.flight.flight_no} 候补队列，当前排位第 {entry.position} 位。',
            'order',
            str(entry.id),
        )


class WaitlistDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, entry_id):
        try:
            entry = WaitlistEntry.objects.get(id=entry_id, user=request.user, status='waiting')
        except WaitlistEntry.DoesNotExist:
            return Response({'error': '候补记录不存在'}, status=404)
        entry.status = 'cancelled'
        entry.save(update_fields=['status'])
        return Response({'message': '已取消候补'})


class FlightAlertDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, alert_id):
        deleted, _ = FlightAlert.objects.filter(id=alert_id, user=request.user).delete()
        if deleted:
            return Response({'message': '已取消订阅'})
        return Response({'error': '订阅不存在'}, status=404)


class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        expire_pending_orders()
        today = timezone.now().date()
        return Response({
            'users': CustomUser.objects.count(),
            'flights': Flight.objects.count(),
            'orders_total': Order.objects.count(),
            'orders_today': Order.objects.filter(created_at__date=today).count(),
            'revenue_total': str(
                Payment.objects.filter(status='success').aggregate(s=Sum('amount'))['s'] or 0
            ),
            'orders_by_status': dict(
                Order.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')
            ),
            'hot_routes': list(
                Flight.objects.values('departure_city', 'arrival_city')
                .annotate(count=Count('orders'))
                .order_by('-count')[:5]
            ),
        })


class ExpireOrdersView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        count = expire_pending_orders()
        return Response({'message': f'已取消 {count} 笔超时订单'})
