from rest_framework import serializers

from apps.flight.serializers import FlightSerializer
from apps.order.models import Coupon, Order, RefundRequest, UserCoupon
from apps.order.services import create_multi_leg_orders, create_round_trip_orders, create_single_order


class OrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'order_id', 'user', 'created_at', 'updated_at', 'paid_at',
            'ticketed_at', 'expires_at', 'discount_amount',
        ]

    def get_is_expired(self, obj):
        return obj.is_expired()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['flight'] = FlightSerializer(instance.flight).data
        return data


class OrderCreateSerializer(serializers.Serializer):
    flight = serializers.IntegerField()
    cabin_class = serializers.ChoiceField(choices=['economy', 'business', 'first'], default='economy')
    seat_number = serializers.CharField(required=False, allow_blank=True, default='')
    passenger_name = serializers.CharField(max_length=50)
    passenger_id_card = serializers.CharField(max_length=18)
    coupon_code = serializers.CharField(required=False, allow_blank=True, default='')
    delay_insurance = serializers.BooleanField(required=False, default=False)

    def create(self, validated_data):
        from apps.flight.models import Flight
        from apps.core.services import expire_pending_orders
        expire_pending_orders()
        flight_id = validated_data.pop('flight')
        flight = Flight.objects.get(pk=flight_id)
        return create_single_order(self.context['request'].user, flight, validated_data)

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class RoundTripCreateSerializer(serializers.Serializer):
    outbound_flight = serializers.IntegerField()
    return_flight = serializers.IntegerField()
    cabin_class = serializers.ChoiceField(choices=['economy', 'business', 'first'], default='economy')
    return_cabin_class = serializers.ChoiceField(
        choices=['economy', 'business', 'first'], required=False
    )
    seat_number = serializers.CharField(required=False, allow_blank=True, default='')
    return_seat_number = serializers.CharField(required=False, allow_blank=True, default='')
    passenger_name = serializers.CharField(max_length=50)
    passenger_id_card = serializers.CharField(max_length=18)
    coupon_code = serializers.CharField(required=False, allow_blank=True, default='')
    delay_insurance = serializers.BooleanField(required=False, default=False)
    return_delay_insurance = serializers.BooleanField(required=False, default=False)

    def create(self, validated_data):
        from apps.flight.models import Flight
        from apps.core.services import expire_pending_orders
        expire_pending_orders()
        outbound = Flight.objects.get(pk=validated_data.pop('outbound_flight'))
        return_flight = Flight.objects.get(pk=validated_data.pop('return_flight'))
        group, out_order, ret_order = create_round_trip_orders(
            self.context['request'].user, outbound, return_flight, validated_data
        )
        return {
            'booking_group_id': group.id,
            'outbound': out_order,
            'return': ret_order,
        }


class MultiLegCreateSerializer(serializers.Serializer):
    flight_ids = serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=4)
    trip_type = serializers.ChoiceField(
        choices=['transfer', 'multi_city'], default='transfer'
    )
    cabin_class = serializers.ChoiceField(choices=['economy', 'business', 'first'], default='economy')
    seat_numbers = serializers.ListField(
        child=serializers.CharField(allow_blank=True), required=False, default=list
    )
    passenger_name = serializers.CharField(max_length=50)
    passenger_id_card = serializers.CharField(max_length=18)
    coupon_code = serializers.CharField(required=False, allow_blank=True, default='')
    delay_insurance_legs = serializers.ListField(
        child=serializers.BooleanField(), required=False, default=list
    )

    def create(self, validated_data):
        from apps.flight.models import Flight
        from apps.core.services import expire_pending_orders
        expire_pending_orders()
        flight_ids = validated_data.pop('flight_ids')
        trip_type = validated_data.pop('trip_type', 'transfer')
        flights = []
        for fid in flight_ids:
            try:
                flights.append(Flight.objects.get(pk=fid))
            except Flight.DoesNotExist:
                raise serializers.ValidationError({'flight_ids': f'航班 {fid} 不存在'})
        group, orders = create_multi_leg_orders(
            self.context['request'].user, flights, validated_data, trip_type=trip_type
        )
        return {'booking_group_id': group.id, 'orders': orders}


class OrderChangeSerializer(serializers.Serializer):
    new_flight = serializers.IntegerField()


class RefundRequestSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)

    class Meta:
        model = RefundRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'amount', 'created_at', 'processed_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'name', 'discount_type', 'discount_value', 'min_amount', 'valid_until']


class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = UserCoupon
        fields = ['id', 'coupon', 'is_used', 'claimed_at']
