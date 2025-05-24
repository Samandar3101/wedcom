from django.urls import path
from .views import (
    TestListAPIView, TestCreateAPIView, TestDetailAPIView, TestUpdateAPIView, TestDeleteAPIView,
    QuestionListAPIView, QuestionCreateAPIView, QuestionDetailAPIView, QuestionUpdateAPIView, QuestionDeleteAPIView,
    AnswerListAPIView, AnswerCreateAPIView, AnswerDetailAPIView, AnswerUpdateAPIView, AnswerDeleteAPIView,
    TestResultListAPIView, TestResultCreateAPIView, TestResultDetailAPIView, TestResultUpdateAPIView, TestResultDeleteAPIView,
    TestResultExportView, TestResultMyResultsView
)

urlpatterns = [
    # Test
    path('tests/', TestListAPIView.as_view(), name='test-list'),
    path('tests/create/', TestCreateAPIView.as_view(), name='test-create'),
    path('tests/<uuid:pk>/', TestDetailAPIView.as_view(), name='test-detail'),
    path('tests/<uuid:pk>/update/', TestUpdateAPIView.as_view(), name='test-update'),
    path('tests/<uuid:pk>/delete/', TestDeleteAPIView.as_view(), name='test-delete'),

    # Question
    path('questions/', QuestionListAPIView.as_view(), name='question-list'),
    path('questions/create/', QuestionCreateAPIView.as_view(), name='question-create'),
    path('questions/<uuid:pk>/', QuestionDetailAPIView.as_view(), name='question-detail'),
    path('questions/<uuid:pk>/update/', QuestionUpdateAPIView.as_view(), name='question-update'),
    path('questions/<uuid:pk>/delete/', QuestionDeleteAPIView.as_view(), name='question-delete'),

    # Answer
    path('answers/', AnswerListAPIView.as_view(), name='answer-list'),
    path('answers/create/', AnswerCreateAPIView.as_view(), name='answer-create'),
    path('answers/<uuid:pk>/', AnswerDetailAPIView.as_view(), name='answer-detail'),
    path('answers/<uuid:pk>/update/', AnswerUpdateAPIView.as_view(), name='answer-update'),
    path('answers/<uuid:pk>/delete/', AnswerDeleteAPIView.as_view(), name='answer-delete'),

    # Test Result
    path('results/', TestResultListAPIView.as_view(), name='testresult-list'),
    path('results/create/', TestResultCreateAPIView.as_view(), name='testresult-create'),
    path('results/<uuid:pk>/', TestResultDetailAPIView.as_view(), name='testresult-detail'),
    path('results/<uuid:pk>/update/', TestResultUpdateAPIView.as_view(), name='testresult-update'),
    path('results/<uuid:pk>/delete/', TestResultDeleteAPIView.as_view(), name='testresult-delete'),
    path('results/<uuid:pk>/export/', TestResultExportView.as_view(), name='testresult-export-result'),
    path('results/my/', TestResultMyResultsView.as_view(), name='testresult-my-results'),
]