from rest_framework import serializers

from apps.core.models import FlightAlert, Notification, PriceWatch, TravelChecklist, WaitlistEntry


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class FlightAlertSerializer(serializers.ModelSerializer):
    flight_no = serializers.CharField(source='flight.flight_no', read_only=True)

    class Meta:
        model = FlightAlert
        fields = ['id', 'flight', 'flight_no', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class WaitlistEntrySerializer(serializers.ModelSerializer):
    flight_no = serializers.CharField(source='flight.flight_no', read_only=True)
    departure_city = serializers.CharField(source='flight.departure_city', read_only=True)
    arrival_city = serializers.CharField(source='flight.arrival_city', read_only=True)
    departure_time = serializers.DateTimeField(source='flight.departure_time', read_only=True)
    position = serializers.IntegerField(read_only=True)
    order_id = serializers.CharField(source='order.order_id', read_only=True, allow_null=True)

    class Meta:
        model = WaitlistEntry
        fields = [
            'id', 'flight', 'flight_no', 'departure_city', 'arrival_city',
            'departure_time', 'passenger_name', 'passenger_id_card', 'cabin_class',
            'status', 'position', 'order', 'order_id', 'created_at',
        ]
        read_only_fields = ['status', 'order', 'created_at']

    def validate(self, attrs):
        flight = attrs.get('flight') or getattr(self.instance, 'flight', None)
        user = self.context['request'].user
        if flight and flight.available_seats > 0:
            raise serializers.ValidationError({'flight': '该航班仍有票，请直接预订'})
        if flight and flight.status != 'normal':
            raise serializers.ValidationError({'flight': '该航班状态不可候补'})
        if WaitlistEntry.objects.filter(user=user, flight=flight, status='waiting').exists():
            raise serializers.ValidationError({'flight': '您已在该航班候补队列中'})
        return attrs

    def create(self, validated_data):
        return WaitlistEntry.objects.create(
            user=self.context['request'].user,
            **validated_data,
        )


class PriceWatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceWatch
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class TravelChecklistSerializer(serializers.ModelSerializer):
    flight_no = serializers.CharField(source='itinerary.flight_no', read_only=True)
    route = serializers.SerializerMethodField()

    class Meta:
        model = TravelChecklist
        fields = ['id', 'itinerary', 'flight_no', 'route', 'items', 'created_at']
        read_only_fields = ['created_at']

    def get_route(self, obj):
        it = obj.itinerary
        return f'{it.departure_city} → {it.arrival_city}'
