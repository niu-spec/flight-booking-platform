from django.urls import path
from apps.user.views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    TokenRefreshView,
    FrequentPassengerListCreateView,
    FrequentPassengerDetailView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('passengers/', FrequentPassengerListCreateView.as_view(), name='passenger-list'),
    path('passengers/<int:pk>/', FrequentPassengerDetailView.as_view(), name='passenger-detail'),
]
