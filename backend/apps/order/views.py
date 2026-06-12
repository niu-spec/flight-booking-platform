from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.core.services import create_notification, expire_pending_orders
from apps.order.models import Coupon, Order, RefundRequest, UserCoupon
from apps.order.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    RoundTripCreateSerializer,
    MultiLegCreateSerializer,
    OrderChangeSerializer,
    RefundRequestSerializer,
    CouponSerializer,
    UserCouponSerializer,
)
from apps.order.services import create_single_order


class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        expire_pending_orders()
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        expire_pending_orders()
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer


class RoundTripCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoundTripCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': '往返订单创建成功',
                'booking_group_id': result['booking_group_id'],
                'outbound': OrderSerializer(result['outbound']).data,
                'return': OrderSerializer(result['return']).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MultiLegCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MultiLegCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': '联程订单创建成功',
                'booking_group_id': result['booking_group_id'],
                'orders': OrderSerializer(result['orders'], many=True).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            if order.is_expired():
                order.cancel()
                return Response({'message': '订单已超时取消', 'order': OrderSerializer(order).data})
            if order.cancel():
                create_notification(
                    request.user, '订单已取消',
                    f'订单 {order.order_id} 已成功取消。', 'order', order.order_id
                )
                return Response({
                    'message': '订单取消成功',
                    'order': OrderSerializer(order).data
                })
            return Response({'error': '订单无法取消'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)


class OrderChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='pending')
        except Order.DoesNotExist:
            return Response({'error': '订单不存在或不可改签'}, status=404)

        serializer = OrderChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        from apps.flight.models import Flight
        new_flight = Flight.objects.get(pk=serializer.validated_data['new_flight'])
        data = {
            'cabin_class': order.cabin_class,
            'seat_number': '',
            'passenger_name': order.passenger_name,
            'passenger_id_card': order.passenger_id_card,
        }
        order.cancel()
        new_order = create_single_order(request.user, new_flight, data, order.booking_group, order.trip_leg)
        create_notification(
            request.user, '改签成功',
            f'订单已改签至航班 {new_flight.flight_no}，新订单号 {new_order.order_id}。',
            'order', new_order.order_id,
        )
        return Response({
            'message': '改签成功',
            'order': OrderSerializer(new_order).data,
        })


class RefundCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='ticketed')
        except Order.DoesNotExist:
            return Response({'error': '订单不存在或不可退款'}, status=404)

        reason = request.data.get('reason', '')
        if not reason:
            return Response({'error': '请填写退款原因'}, status=400)

        refund = RefundRequest.objects.create(
            order=order,
            user=request.user,
            reason=reason,
            amount=order.total_amount,
        )
        order.refund()
        refund.status = 'approved'
        refund.processed_at = timezone.now()
        refund.save()
        create_notification(
            request.user, '退款成功',
            f'订单 {order.order_id} 退款 ¥{order.total_amount} 已处理。',
            'refund', order.order_id,
        )
        return Response({
            'message': '退款申请已通过',
            'refund': RefundRequestSerializer(refund).data,
            'order': OrderSerializer(order).data,
        })


class CouponListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CouponSerializer

    def get_queryset(self):
        return Coupon.objects.filter(is_active=True)


class UserCouponListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCouponSerializer

    def get_queryset(self):
        return UserCoupon.objects.filter(user=self.request.user, is_used=False)


class ClaimCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': '请输入优惠码'}, status=400)
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({'error': '优惠券不存在'}, status=404)
        if not coupon.is_valid():
            return Response({'error': '优惠券已失效'}, status=400)
        obj, created = UserCoupon.objects.get_or_create(user=request.user, coupon=coupon)
        if not created:
            return Response({'error': '您已领取过该优惠券'}, status=400)
        return Response({
            'message': '领取成功',
            'coupon': UserCouponSerializer(obj).data,
        })


class TicketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='ticketed')
        except Order.DoesNotExist:
            return Response({'error': '电子客票不存在'}, status=404)
        flight = order.flight
        ticket_no = f'TKT{order.order_id}'
        return Response({
            'ticket_no': ticket_no,
            'order_id': order.order_id,
            'passenger_name': order.passenger_name,
            'passenger_id_card': order.passenger_id_card,
            'seat_number': order.seat_number or '待分配',
            'cabin_class': order.cabin_class,
            'flight_no': flight.flight_no,
            'airline': flight.airline,
            'departure_city': flight.departure_city,
            'arrival_city': flight.arrival_city,
            'departure_time': flight.departure_time,
            'arrival_time': flight.arrival_time,
            'ticketed_at': order.ticketed_at,
            'qr_payload': ticket_no,
        })


class ShareTripView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='ticketed')
        except Order.DoesNotExist:
            return Response({'error': '仅已出票订单可分享'}, status=404)
        flight = order.flight
        from apps.core.weather import get_weather
        weather = get_weather(flight.arrival_city)
        dep = flight.departure_time.strftime('%m月%d日 %H:%M')
        arr = flight.arrival_time.strftime('%H:%M')
        share_text = (
            f'✈ 我的行程分享\n'
            f'{flight.departure_city} → {flight.arrival_city}\n'
            f'航班 {flight.flight_no}（{flight.airline}）\n'
            f'{dep} 出发，{arr} 到达\n'
            f'乘客：{order.passenger_name}  座位：{order.seat_number or "待分配"}'
        )
        if weather:
            share_text += f'\n目的地天气：{weather["icon"]} {weather["condition"]} {weather["temperature"]}°C'
        return Response({
            'title': f'{flight.departure_city} → {flight.arrival_city}',
            'subtitle': f'{flight.flight_no} · {order.passenger_name}',
            'share_text': share_text,
            'qr_payload': f'TKT{order.order_id}',
            'weather': weather,
            'flight_no': flight.flight_no,
            'departure_city': flight.departure_city,
            'arrival_city': flight.arrival_city,
            'departure_time': flight.departure_time,
            'arrival_time': flight.arrival_time,
        })
