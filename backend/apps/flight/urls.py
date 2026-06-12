from django.urls import path
from apps.flight.views import (
    FlightListView,
    FlightDetailView,
    FlightSearchView,
    FlightStatusUpdateView,
    FlightSeatMapView,
    PriceCalendarView,
    FlightReviewListView,
    FlightReviewCreateView,
    TransferSearchView,
)

urlpatterns = [
    path('', FlightListView.as_view(), name='flight-list'),
    path('search/', FlightSearchView.as_view(), name='flight-search'),
    path('price-calendar/', PriceCalendarView.as_view(), name='price-calendar'),
    path('search-transfer/', TransferSearchView.as_view(), name='flight-search-transfer'),
    path('reviews/', FlightReviewCreateView.as_view(), name='flight-review-create'),
    path('<int:flight_id>/reviews/', FlightReviewListView.as_view(), name='flight-review-list'),
    path('<int:id>/', FlightDetailView.as_view(), name='flight-detail'),
    path('<int:flight_id>/seats/', FlightSeatMapView.as_view(), name='flight-seats'),
    path('<int:flight_id>/update-status/', FlightStatusUpdateView.as_view(), name='flight-update-status'),
]
