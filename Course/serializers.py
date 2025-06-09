from rest_framework import serializers
from Course import models
from CustomerUser.models import CustomerUser


# === CATEGORY ===
class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = 'id', 'name', 'icon'


# === COURSE ===
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = '__all__'

# === MODULE ===
class ModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module
        fields = '__all__'

class ModuleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module
        fields = 'id', 'title', 'order', 'course'

class ModuleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module
        fields = 'id', 'title', 'course'

class ModulePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module
        fields = 'id', 'title', 'course', 'order'


# === LESSON ===
class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        fields = '__all__'

class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        fields = 'id', 'title', 'module', 'order'

class LessonDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        fields = 'id', 'title', 'module', 'content', 'video', 'duration'

class LessonPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson   
        fields = 'id', 'title', 'module', 'content', 'video', 'duration', 'order'


# === PROGRESS ===
class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Progress
        fields = '__all__'

class ProgressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Progress
        fields = 'completion_date','is_completed'

# === REVIEW ===
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = '__all__'

