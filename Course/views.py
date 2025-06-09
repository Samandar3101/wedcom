from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from Course import serializers, models
from .permissions import IsCustomAdminUser



# === CATEGORY ===
class CategoryListAPIView(APIView):
    def get(self, request):
        categories = models.Category.objects.all()
        serializer = serializers.CategoryListSerializer(categories, many=True)
        return Response(serializer.data)


class CategoryCreateAPIView(APIView):
    def post(self, request):
        # Faqat admin foydalanuvchi ruxsat etiladi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.CategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    def get(self, request, pk):
        category = get_object_or_404(models.Category, pk=pk)
        serializer = serializers.CategoryListSerializer(category)
        return Response(serializer.data)


class CategoryPutAPIView(APIView):
    def put(self, request, pk):
        # Faqat admin foydalanuvchi ruxsat etiladi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        category = get_object_or_404(models.Category, pk=pk)
        serializer = serializers.CategoryCreateSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDeleteAPIView(APIView):
    def delete(self, request, pk):
        # Faqat admin foydalanuvchi ruxsat etiladi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        category = get_object_or_404(models.Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# === COURSE ===
class CourseListAPIView(APIView):
    def get(self, request):
        courses = models.Course.objects.all()
        serializer = serializers.CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseCreateAPIView(APIView):
    def post(self, request):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailAPIView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(models.Course, pk=pk)
        serializer = serializers.CourseSerializer(course)
        return Response(serializer.data)


class CoursePutAPIView(APIView):
    def put(self, request, pk):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        course = get_object_or_404(models.Course, pk=pk)
        serializer = serializers.CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDeleteAPIView(APIView):
    def delete(self, request, pk):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        course = get_object_or_404(models.Course, pk=pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === MODULE ===
class ModuleListAPIView(APIView):
    def get(self, request):
        
        modules = models.Module.objects.all()
        serializer = serializers.ModuleListSerializer(modules, many=True)
        return Response(serializer.data)

class ModuleCreateAPIView(APIView):
    def post(self, request):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.ModuleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ModuleDetailAPIView(APIView):
    def get(self, request, pk):
        module = get_object_or_404(models.Module, pk=pk)
        serializer = serializers.ModuleDetailSerializer(module)
        return Response(serializer.data)

class ModulePutAPIView(APIView):
    def put(self, request, pk):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)

        module = get_object_or_404(models.Module, pk=pk)
        serializer = serializers.ModulePutSerializer(module, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ModuleDeleteAPIView(APIView):
    def delete(self, request, pk):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)
    
        module = get_object_or_404(models.Module, pk=pk)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === LESSON ===
class LessonListAPIView(APIView):
    def get(self, request):
        lessons = models.Lesson.objects.all()
        serializer = serializers.LessonListSerializer(lessons, many=True)
        return Response(serializer.data)

class LessonCreateAPIView(APIView):
    def post(self, request):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = serializers.LessonCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LessonDetailAPIView(APIView):
    def get(self, request, pk):
        lesson = get_object_or_404(models.Lesson, pk=pk)
        serializer = serializers.LessonDetailSerializer(lesson)
        return Response(serializer.data)

class LessonPutAPIView(APIView):
    def put(self, request, pk):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)
        lesson = get_object_or_404(models.Lesson, pk=pk)
        serializer = serializers.LessonPutSerializer(lesson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LessonDeleteAPIView(APIView):
    def delete(self, request, pk):
        # Faqat admin foydalanuvchi
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)
        lesson = get_object_or_404(models.Lesson, pk=pk)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === PROGRESS ===
class ProgressListAPIView(APIView):
    def get(self, request):
        progresses = models.Progress.objects.all()
        serializer = serializers.ProgressSerializer(progresses, many=True)
        return Response(serializer.data)

class ProgresscreateAPIView(APIView):
    def post(self, request):
        serializer = serializers.ProgressCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProgressDetailAPIView(APIView):
    def get(self, request, pk):
        progress = get_object_or_404(models.Progress, pk=pk)
        serializer = serializers.ProgressSerializer(progress)
        return Response(serializer.data)


# === REVIEW ===
class ReviewListAPIView(APIView):
    def get(self, request):
        reviews = models.Review.objects.all()
        serializer = serializers.ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class ReviewCreateAPIView(APIView):
    def post(self, request):
        serializer = serializers.ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewDetailAPIView(APIView):
    def get(self, request, pk):
        review = get_object_or_404(models.Review, pk=pk)
        serializer = serializers.ReviewSerializer(review)
        return Response(serializer.data)



class ReviewDeleteAPIView(APIView):
    def delete(self, request, pk):
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarishga ruxsat yo‘q."},
                            status=status.HTTP_403_FORBIDDEN)
        review = get_object_or_404(models.Review, pk=pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
