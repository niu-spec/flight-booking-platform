from django.contrib import admin
from apps.payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'amount', 'payment_method', 
                    'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['payment_id', 'order__order_id', 'transaction_id']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['payment_id', 'transaction_id', 'callback_time', 'callback_data', 
                       'created_at', 'updated_at']
