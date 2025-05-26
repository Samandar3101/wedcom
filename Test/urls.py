from django.urls import path
from .views import (
    TestListAPIView, TestDetailAPIView,
    QuestionListAPIView, QuestionDetailAPIView,
    TestResultListAPIView, TestResultDetailAPIView,
    TestResultExportView
)

urlpatterns = [
    # Test URLs
    path('tests/', TestListAPIView.as_view(), name='test-list'),
    path('tests/<uuid:pk>/', TestDetailAPIView.as_view(), name='test-detail'),
    
    # Question URLs
    path('questions/', QuestionListAPIView.as_view(), name='question-list'),
    path('questions/<uuid:pk>/', QuestionDetailAPIView.as_view(), name='question-detail'),
    
    # Test Result URLs
    path('results/', TestResultListAPIView.as_view(), name='testresult-list'),
    path('results/<uuid:pk>/', TestResultDetailAPIView.as_view(), name='testresult-detail'),
    path('results/export/', TestResultExportView.as_view(), name='testresult-export'),
]