from django.urls import path

from apps.core.views import (
    AdminStatsView,
    ExpireOrdersView,
    FlightAlertDeleteView,
    FlightAlertListCreateView,
    WaitlistListCreateView,
    WaitlistDeleteView,
    NotificationListView,
    NotificationReadAllView,
    NotificationReadView,
)
from apps.core.innovation_views import (
    ChatAssistantView,
    PriceWatchListCreateView,
    PriceWatchDeleteView,
    FlightCompareView,
    TravelChecklistView,
    CheckPriceWatchesView,
    WeatherView,
)

urlpatterns = [
    path('chat/', ChatAssistantView.as_view(), name='chat-assistant'),
    path('weather/', WeatherView.as_view(), name='weather'),
    path('price-watches/', PriceWatchListCreateView.as_view(), name='price-watch-list'),
    path('price-watches/<int:watch_id>/', PriceWatchDeleteView.as_view(), name='price-watch-delete'),
    path('price-watches/check/', CheckPriceWatchesView.as_view(), name='price-watch-check'),
    path('flights/compare/', FlightCompareView.as_view(), name='flight-compare'),
    path('checklists/', TravelChecklistView.as_view(), name='checklist-list'),
    path('checklists/<int:itinerary_id>/', TravelChecklistView.as_view(), name='checklist-detail'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('notifications/read-all/', NotificationReadAllView.as_view(), name='notification-read-all'),
    path('flight-alerts/', FlightAlertListCreateView.as_view(), name='flight-alert-list'),
    path('flight-alerts/<int:alert_id>/', FlightAlertDeleteView.as_view(), name='flight-alert-delete'),
    path('waitlist/', WaitlistListCreateView.as_view(), name='waitlist-list'),
    path('waitlist/<int:entry_id>/', WaitlistDeleteView.as_view(), name='waitlist-delete'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/expire-orders/', ExpireOrdersView.as_view(), name='expire-orders'),
]
