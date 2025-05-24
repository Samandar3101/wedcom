from django_filters import rest_framework as filters
from .models import Test, TestResult

class TestFilter(filters.FilterSet):
    """
    Filter for Test model
    """
    min_duration = filters.NumberFilter(field_name="duration_minutes", lookup_expr='gte')
    max_duration = filters.NumberFilter(field_name="duration_minutes", lookup_expr='lte')
    min_passing_score = filters.NumberFilter(field_name="passing_score", lookup_expr='gte')
    max_passing_score = filters.NumberFilter(field_name="passing_score", lookup_expr='lte')
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    course = filters.NumberFilter(field_name="course", lookup_expr='exact')
    created_by = filters.NumberFilter(field_name="created_by", lookup_expr='exact')
    is_active = filters.BooleanFilter(field_name="is_active", lookup_expr='exact')

    class Meta:
        model = Test
        fields = [
            'min_duration', 'max_duration', 'min_passing_score', 'max_passing_score',
            'created_after', 'created_before', 'course', 'created_by', 'is_active'
        ]

class TestResultFilter(filters.FilterSet):
    """
    Filter for TestResult model
    """
    min_score = filters.NumberFilter(field_name="score", lookup_expr='gte')
    max_score = filters.NumberFilter(field_name="score", lookup_expr='lte')
    started_after = filters.DateTimeFilter(field_name="started_at", lookup_expr='gte')
    started_before = filters.DateTimeFilter(field_name="started_at", lookup_expr='lte')
    completed_after = filters.DateTimeFilter(field_name="completed_at", lookup_expr='gte')
    completed_before = filters.DateTimeFilter(field_name="completed_at", lookup_expr='lte')
    test = filters.NumberFilter(field_name="test", lookup_expr='exact')
    user = filters.NumberFilter(field_name="user", lookup_expr='exact')
    passed = filters.BooleanFilter(field_name="passed", lookup_expr='exact')
    test_title = filters.CharFilter(field_name="test__title", lookup_expr='icontains')
    user_email = filters.CharFilter(field_name="user__email", lookup_expr='icontains')
    duration = filters.NumberFilter(method='filter_duration')
    score_range = filters.CharFilter(method='filter_score_range')

    class Meta:
        model = TestResult
        fields = [
            'min_score', 'max_score', 'started_after', 'started_before',
            'completed_after', 'completed_before', 'test', 'user', 'passed',
            'test_title', 'user_email', 'duration', 'score_range'
        ]

    def filter_duration(self, queryset, name, value):
        """Filter by test duration in minutes"""
        return queryset.filter(
            test__duration_minutes=value
        )

    def filter_score_range(self, queryset, name, value):
        """Filter by score range (e.g. '0-50', '50-70', '70-100')"""
        try:
            min_score, max_score = map(int, value.split('-'))
            return queryset.filter(score__gte=min_score, score__lt=max_score)
        except (ValueError, TypeError):
            return queryset 