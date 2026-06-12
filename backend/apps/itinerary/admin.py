from django.contrib import admin
from apps.itinerary.models import Itinerary


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['itinerary_id', 'user', 'flight_no', 'departure_city', 
                    'arrival_city', 'departure_time', 'status']
    list_filter = ['status']
    search_fields = ['itinerary_id', 'user__username', 'flight_no']
    date_hierarchy = 'departure_time'
    ordering = ['-departure_time']
    readonly_fields = ['itinerary_id', 'created_at', 'updated_at']
