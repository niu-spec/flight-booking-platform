from django.urls import path
from apps.order.views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderCancelView,
    RoundTripCreateView,
    MultiLegCreateView,
    OrderChangeView,
    RefundCreateView,
    CouponListView,
    UserCouponListView,
    ClaimCouponView,
    TicketView,
    ShareTripView,
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('create-roundtrip/', RoundTripCreateView.as_view(), name='order-roundtrip'),
    path('create-multileg/', MultiLegCreateView.as_view(), name='order-multileg'),
    path('coupons/', CouponListView.as_view(), name='coupon-list'),
    path('my-coupons/', UserCouponListView.as_view(), name='my-coupon-list'),
    path('claim-coupon/', ClaimCouponView.as_view(), name='claim-coupon'),
    path('<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    path('<int:order_id>/change/', OrderChangeView.as_view(), name='order-change'),
    path('<int:order_id>/refund/', RefundCreateView.as_view(), name='order-refund'),
    path('<int:order_id>/ticket/', TicketView.as_view(), name='order-ticket'),
    path('<int:order_id>/share/', ShareTripView.as_view(), name='order-share'),
]
