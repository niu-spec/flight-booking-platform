from django.contrib import admin
from apps.flight.models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_no', 'airline', 'departure_city', 'arrival_city', 
                    'departure_time', 'base_price', 'available_seats', 'status']
    list_filter = ['status', 'airline']
    search_fields = ['flight_no', 'departure_city', 'arrival_city']
    date_hierarchy = 'departure_time'
    ordering = ['-departure_time']
    
    actions = ['make_normal', 'make_delayed', 'make_cancelled']
    
    def make_normal(self, request, queryset):
        count = queryset.update(status='normal')
        self.message_user(request, f'{count} 个航班已设置为正常')
    make_normal.short_description = '设置为正常'
    
    def make_delayed(self, request, queryset):
        count = queryset.update(status='delayed')
        self.message_user(request, f'{count} 个航班已设置为延误')
    make_delayed.short_description = '设置为延误'
    
    def make_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f'{count} 个航班已设置为取消')
    make_cancelled.short_description = '设置为取消'
