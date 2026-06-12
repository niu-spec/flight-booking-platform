from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.core.services import create_notification
from apps.payment.models import Payment, Invoice
from apps.payment.serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentCallbackSerializer,
    InvoiceSerializer,
)
from apps.order.models import Order
from apps.itinerary.models import Itinerary


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='pending')
            
            if hasattr(order, 'payment'):
                return Response({
                    'message': '支付请求已发起',
                    'payment': PaymentSerializer(order.payment).data,
                }, status=status.HTTP_200_OK)
            
            serializer = PaymentCreateSerializer(data=request.data, context={'order': order})
            if serializer.is_valid():
                payment = serializer.save()
                
                result = payment.execute_pay()

                if settings.DEBUG:
                    payment.handle_callback({
                        'success': True,
                        'transaction_id': f'DEMO{payment.payment_id}',
                        'message': 'demo payment',
                    })
                    Itinerary.create_from_order(payment.order)
                    payment.refresh_from_db()
                    order.refresh_from_db()
                    create_notification(
                        request.user, '支付成功',
                        f'订单 {order.order_id} 已支付并出票。',
                        'payment', payment.payment_id,
                    )
                    level, label = request.user.add_points(order.total_amount)
                    create_notification(
                        request.user, f'积分到账 +{int(order.total_amount)}',
                        f'恭喜升级为{label}！当前积分 {request.user.points}。',
                        'system', '',
                    )
                    from apps.core.innovation import generate_checklist
                    from apps.core.models import TravelChecklist
                    from apps.itinerary.models import Itinerary
                    itin = Itinerary.objects.filter(order=order).first()
                    if itin:
                        TravelChecklist.objects.get_or_create(
                            user=request.user,
                            itinerary=itin,
                            defaults={'items': generate_checklist(itin)},
                        )
                
                return Response({
                    'message': '支付成功，已出票' if settings.DEBUG else '支付请求已发起',
                    'payment': PaymentSerializer(payment).data,
                    'gateway_response': result
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在或无法支付'}, status=status.HTTP_404_NOT_FOUND)


class PaymentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


class PaymentCallbackView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            
            serializer = PaymentCallbackSerializer(data=request.data)
            if serializer.is_valid():
                success = payment.handle_callback(serializer.validated_data)
                
                if success:
                    Itinerary.create_from_order(payment.order)
                    
                    return Response({
                        'message': '支付成功，已出票',
                        'payment': PaymentSerializer(payment).data
                    })
                return Response({
                    'message': '支付失败',
                    'payment': PaymentSerializer(payment).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'error': '支付记录不存在'}, status=status.HTTP_404_NOT_FOUND)


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(pk=payment_id, order__user=request.user)
            return Response({
                'id': payment.id,
                'payment_id': payment.payment_id,
                'status': payment.status,
                'order_status': payment.order.status,
            })
        except Payment.DoesNotExist:
            return Response({'error': '支付记录不存在'}, status=404)


class InvoiceCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='ticketed')
        except Order.DoesNotExist:
            return Response({'error': '订单不存在或不可开票'}, status=404)
        if hasattr(order, 'invoice'):
            return Response({'message': '已申请过发票', 'invoice': InvoiceSerializer(order.invoice).data})
        title = request.data.get('title')
        if not title:
            return Response({'error': '请填写发票抬头'}, status=400)
        invoice = Invoice.objects.create(
            order=order,
            title=title,
            tax_number=request.data.get('tax_number', ''),
            amount=order.total_amount,
            status='issued',
        )
        create_notification(
            request.user, '发票已开具',
            f'订单 {order.order_id} 的电子发票已开具。',
            'order', order.order_id,
        )
        return Response({'message': '发票申请成功', 'invoice': InvoiceSerializer(invoice).data})


class InvoiceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(order__user=self.request.user)
