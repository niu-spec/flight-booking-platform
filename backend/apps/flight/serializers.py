from rest_framework import serializers
from apps.flight.models import Flight, FlightReview
from apps.core.innovation import calc_carbon_kg


class FlightSerializer(serializers.ModelSerializer):
    is_available = serializers.ReadOnlyField()
    carbon_kg = serializers.SerializerMethodField()
    recommend_tag = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = '__all__'

    def get_carbon_kg(self, obj):
        return calc_carbon_kg(obj)

    def get_recommend_tag(self, obj):
        labels = self.context.get('recommend_labels', {})
        return labels.get(str(obj.id), '')


class FlightReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    flight_no = serializers.CharField(source='flight.flight_no', read_only=True)

    class Meta:
        model = FlightReview
        fields = ['id', 'flight', 'flight_no', 'order', 'rating', 'content', 'username', 'created_at']
        read_only_fields = ['user', 'created_at']


class FlightReviewCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        from apps.order.models import Order
        user = self.context['request'].user
        try:
            order = Order.objects.get(id=attrs['order_id'], user=user, status='ticketed')
        except Order.DoesNotExist:
            raise serializers.ValidationError({'order_id': '仅已出票订单可评价'})
        if FlightReview.objects.filter(user=user, order=order).exists():
            raise serializers.ValidationError({'order_id': '该订单已评价'})
        attrs['order'] = order
        return attrs

    def create(self, validated_data):
        order = validated_data['order']
        return FlightReview.objects.create(
            user=self.context['request'].user,
            flight=order.flight,
            order=order,
            rating=validated_data['rating'],
            content=validated_data.get('content', ''),
        )


class FlightSearchSerializer(serializers.Serializer):
    departure_city = serializers.CharField(required=False)
    arrival_city = serializers.CharField(required=False)
    departure_date = serializers.DateField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
