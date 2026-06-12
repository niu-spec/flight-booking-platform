"""URL configuration for flight booking platform."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.user.urls')),
    path('api/flights/', include('apps.flight.urls')),
    path('api/orders/', include('apps.order.urls')),
    path('api/payments/', include('apps.payment.urls')),
    path('api/itineraries/', include('apps.itinerary.urls')),
    path('api/', include('apps.core.urls')),
]
