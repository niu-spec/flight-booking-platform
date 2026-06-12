from rest_framework import serializers
from apps.itinerary.models import Itinerary


class ItinerarySerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    
    class Meta:
        model = Itinerary
        fields = '__all__'
        read_only_fields = ['itinerary_id', 'user', 'order', 'created_at', 'updated_at']
