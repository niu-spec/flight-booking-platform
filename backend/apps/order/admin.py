from django.contrib import admin
from apps.order.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'flight', 'cabin_class', 
                    'total_amount', 'status', 'created_at']
    list_filter = ['status', 'cabin_class']
    search_fields = ['order_id', 'user__username', 'flight__flight_no']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['order_id', 'created_at', 'updated_at', 'paid_at', 'ticketed_at']
    
    actions = ['make_cancelled']
    
    def make_cancelled(self, request, queryset):
        for order in queryset:
            order.cancel()
        self.message_user(request, f'{queryset.count()} 个订单已取消')
    make_cancelled.short_description = '取消订单'
