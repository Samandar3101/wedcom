from django.urls import path
from .views import (
    PaymentListView,
    PaymentDetailView,
    PaymentRefundView,
    PaymentCancelView,
    PaymentWebhookView
)

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/<uuid:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/<uuid:pk>/refund/', PaymentRefundView.as_view(), name='payment-refund'),
    path('payments/<uuid:pk>/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('payments/webhook/<str:provider>/', PaymentWebhookView.as_view(), name='payment-webhook'),
]