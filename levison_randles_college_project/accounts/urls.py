from django.urls import path
from .views import RegisterView, UserProfileView, LoginView # Import LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='account_register'),
    path('login/', LoginView.as_view(), name='account_login'), # Added login path
    path('profile/', UserProfileView.as_view(), name='account_profile'),
]
