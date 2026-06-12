from django.urls import path
from apps.payment.views import (
    PaymentCreateView,
    PaymentDetailView,
    PaymentCallbackView,
    PaymentStatusView,
    InvoiceCreateView,
    InvoiceListView,
)

urlpatterns = [
    path('create/<int:order_id>/', PaymentCreateView.as_view(), name='payment-create'),
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoice/<int:order_id>/', InvoiceCreateView.as_view(), name='invoice-create'),
    path('<int:id>/status/', PaymentStatusView.as_view(), name='payment-status'),
    path('<int:id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('callback/<str:payment_id>/', PaymentCallbackView.as_view(), name='payment-callback'),
]
