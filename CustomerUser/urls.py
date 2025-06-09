from django.urls import path
from .views import (
    CustomerUserView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    VerifyEmailView,
    VerifyPhoneView,
    NotificationView,
    MarkNotificationReadView
)

urlpatterns = [
    path('users/me/', CustomerUserView.as_view(), name='user-profile'),
    path('users/<int:pk>/', CustomerUserView.as_view(), name='user-detail'),
    path('users/', CustomerUserView.as_view(), name='user-list'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('notifications/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
] 