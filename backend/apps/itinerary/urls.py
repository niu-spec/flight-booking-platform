from django.urls import path
from apps.itinerary.views import (
    ItineraryListView,
    ItineraryDetailView,
    ItineraryRefreshView
)

urlpatterns = [
    path('', ItineraryListView.as_view(), name='itinerary-list'),
    path('<int:id>/', ItineraryDetailView.as_view(), name='itinerary-detail'),
    path('<int:itinerary_id>/refresh/', ItineraryRefreshView.as_view(), name='itinerary-refresh'),
]
