from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, UserPaymentsView
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('course/<uuid:course_id>/payments/', PaymentViewSet.as_view({'get': 'course_payments'}), name='payment-course-payments'),
    path('payments/verify/<str:payment_id>/', PaymentViewSet.as_view({'post': 'verify_payment'}), name='payment-verify'),
    path('payments/checkout/<str:payment_id>/', PaymentViewSet.as_view({'get': 'checkout'}), name='payment-checkout'),
    path('payments/webhook/<str:provider>/', PaymentViewSet.as_view({'post': 'webhook'}), name='payment-webhook'),
    path('payments/my/', UserPaymentsView.as_view(), name='user-payments'),
]