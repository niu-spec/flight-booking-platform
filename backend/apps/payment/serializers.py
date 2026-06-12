from rest_framework import serializers
from apps.payment.models import Payment, Invoice


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payment_id', 'order', 'transaction_id', 'callback_time', 'callback_data', 'created_at', 'updated_at']


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method']
    
    def create(self, validated_data):
        order = self.context['order']
        
        payment = Payment.objects.create(
            payment_id=Payment.generate_payment_id(),
            order=order,
            amount=order.total_amount,
            payment_method=validated_data['payment_method']
        )
        
        return payment


class PaymentCallbackSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    transaction_id = serializers.CharField()
    message = serializers.CharField(required=False, default='')


class InvoiceSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['order', 'amount', 'status', 'created_at']
