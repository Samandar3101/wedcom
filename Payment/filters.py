from django_filters import rest_framework as filters
from .models import Payment

class PaymentFilter(filters.FilterSet):
    """
    Filter for Payment model
    """
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr='lte')
    start_date = filters.DateTimeFilter(field_name="payment_date", lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name="payment_date", lookup_expr='lte')
    status = filters.CharFilter(field_name="status", lookup_expr='exact')
    method = filters.CharFilter(field_name="method", lookup_expr='exact')
    course = filters.NumberFilter(field_name="course", lookup_expr='exact')
    user = filters.NumberFilter(field_name="user", lookup_expr='exact')
    is_refunded = filters.BooleanFilter(field_name="refund_date", lookup_expr='isnull', exclude=True)

    class Meta:
        model = Payment
        fields = [
            'min_amount', 'max_amount', 'start_date', 'end_date',
            'status', 'method', 'course', 'user', 'is_refunded'
        ] 