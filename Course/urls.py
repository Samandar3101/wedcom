from django.urls import path
from .views import (
    CategoryListAPIView, CategoryCreateAPIView, CategoryDetailAPIView, CategoryPutAPIView, CategoryDeleteAPIView,
    CourseListAPIView, CourseCreateAPIView, CourseDetailAPIView, CoursePutAPIView, CourseDeleteAPIView,
    ModuleListAPIView, ModuleCreateAPIView, ModuleDetailAPIView, ModulePutAPIView, ModuleDeleteAPIView,
    LessonCreateAPIView, LessonListAPIView, LessonDetailAPIView, LessonPutAPIView, LessonDeleteAPIView,
    ProgressListAPIView, ProgressDetailAPIView,ProgresscreateAPIView,
    ReviewListAPIView, ReviewCreateAPIView, ReviewDetailAPIView, ReviewDeleteAPIView
)

urlpatterns = [
    # Category
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('categories/<uuid:pk>/put/', CategoryPutAPIView.as_view(), name='category-put'),
    path('categories/<uuid:pk>/delete/', CategoryDeleteAPIView.as_view(), name='category-delete'),

    # Course
    path('courses/', CourseListAPIView.as_view(), name='course-list'),
    path('courses/create/', CourseCreateAPIView.as_view(), name='course-create'),
    path('courses/<uuid:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('courses/<uuid:pk>/put/', CoursePutAPIView.as_view(), name='course-put'),
    path('courses/<uuid:pk>/delete/', CourseDeleteAPIView.as_view(), name='course-delete'),

    # Module
    path('modules/', ModuleListAPIView.as_view(), name='module-list'),
    path('modules/create/', ModuleCreateAPIView.as_view(), name='module-create'),
    path('modules/<uuid:pk>/', ModuleDetailAPIView.as_view(), name='module-detail'),
    path('modules/<uuid:pk>/put/', ModulePutAPIView.as_view(), name='module-put'),
    path('modules/<uuid:pk>/delete/', ModuleDeleteAPIView.as_view(), name='module-delete'),

    # Lesson
    path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lessons/<uuid:pk>/', LessonDetailAPIView.as_view(), name='lesson-detail'),
    path('lessons/<uuid:pk>/put/', LessonPutAPIView.as_view(), name='lesson-put'),
    path('lessons/<uuid:pk>/delete/', LessonDeleteAPIView.as_view(), name='lesson-delete'),

    # Progress
    path('progress/', ProgressListAPIView.as_view(), name='progress-list'),
    path('progress/<uuid:pk>/', ProgressDetailAPIView.as_view(), name='progress-detail'),
    path('progress/create/', LessonCreateAPIView.as_view(), name='progress-create'),

    # Review
    path('reviews/', ReviewListAPIView.as_view(), name='review-list'),
    path('reviews/create/', ReviewCreateAPIView.as_view(), name='review-create'),
    path('reviews/<uuid:pk>/', ReviewDetailAPIView.as_view(), name='review-detail'),
    path('reviews/<uuid:pk>/delete/', ReviewDeleteAPIView.as_view(), name='review-delete'),
]
