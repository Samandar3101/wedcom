from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Test, Question, Answer, TestResult
from .serializers import TestSerializer, QuestionSerializer, QuestionCreateSerializer, AnswerSerializer, TestResultSerializer
from .permissions import IsCourseInstructorOrAdmin
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

# === TEST ===
class TestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Test.objects.all()
            course_id = request.query_params.get('course')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering', '-created_at')

            if course_id:
                queryset = queryset.filter(course_id=course_id)
            if search:
                queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
            if ordering:
                queryset = queryset.order_by(ordering)

            # Filter based on user role
            if request.user.role == 'student':
                queryset = queryset.filter(is_active=True)
            elif request.user.role == 'teacher':
                queryset = queryset.filter(course__instructor=request.user)

            serializer = TestSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Test list error: {str(e)}")
            return Response({"detail": "Testlarni olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = TestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Test create error: {str(e)}")
            return Response({"detail": "Test yaratishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            test = get_object_or_404(Test, pk=pk)
            serializer = TestSerializer(test)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Test retrieve error: {str(e)}")
            return Response({"detail": "Test ma'lumotlarini olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            test = get_object_or_404(Test, pk=pk)
            serializer = TestSerializer(test, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Test update error: {str(e)}")
            return Response({"detail": "Test ma'lumotlarini yangilashda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            test = get_object_or_404(Test, pk=pk)
            test.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Test delete error: {str(e)}")
            return Response({"detail": "Testni o'chirishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# === QUESTION ===
class QuestionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Question.objects.all()
            test_id = request.query_params.get('test')
            ordering = request.query_params.get('ordering', 'order')

            if test_id:
                queryset = queryset.filter(test_id=test_id)
            if ordering:
                queryset = queryset.order_by(ordering)

            serializer = QuestionSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Question list error: {str(e)}")
            return Response({"detail": "Savollarni olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = QuestionCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Question create error: {str(e)}")
            return Response({"detail": "Savol yaratishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Question retrieve error: {str(e)}")
            return Response({"detail": "Savol ma'lumotlarini olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            serializer = QuestionSerializer(question, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Question update error: {str(e)}")
            return Response({"detail": "Savol ma'lumotlarini yangilashda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Question delete error: {str(e)}")
            return Response({"detail": "Savolni o'chirishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# === ANSWER ===
class AnswerListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Answer.objects.all()
            question_id = request.query_params.get('question')
            if question_id:
                queryset = queryset.filter(question_id=question_id)
            serializer = AnswerSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Answer list error: {str(e)}")
            return Response({"detail": "Javoblarni olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnswerCreateAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            question = get_object_or_404(Question, pk=request.data.get('question'))
            serializer.save(question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnswerDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = AnswerSerializer(answer)
        return Response(serializer.data)

class AnswerUpdateAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def put(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = AnswerSerializer(answer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnswerDeleteAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def delete(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === TEST RESULT ===
class TestResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = TestResult.objects.all()
            test_id = request.query_params.get('test')
            user_id = request.query_params.get('user')

            if test_id:
                queryset = queryset.filter(test_id=test_id)
            if user_id:
                queryset = queryset.filter(user_id=user_id)

            serializer = TestResultSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Test result list error: {str(e)}")
            return Response({"detail": "Test natijalarini olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = TestResultSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Test result create error: {str(e)}")
            return Response({"detail": "Test natijasini yaratishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestResultDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            result = get_object_or_404(TestResult, pk=pk)
            serializer = TestResultSerializer(result)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Test result retrieve error: {str(e)}")
            return Response({"detail": "Test natijasini olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            result = get_object_or_404(TestResult, pk=pk)
            serializer = TestResultSerializer(result, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Test result update error: {str(e)}")
            return Response({"detail": "Test natijasini yangilashda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            result = get_object_or_404(TestResult, pk=pk)
            result.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Test result delete error: {str(e)}")
            return Response({"detail": "Test natijasini o'chirishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestResultExportView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def get(self, request, pk):
        try:
            result = get_object_or_404(TestResult, pk=pk)
            
            # Create CSV content
            import csv
            from io import StringIO
            from django.http import HttpResponse
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Test', 'Student', 'Score', 'Passed', 'Started At', 'Completed At'])
            
            # Write data
            writer.writerow([
                result.test.title,
                result.user.email,
                result.score,
                'Yes' if result.passed else 'No',
                result.started_at,
                result.completed_at
            ])
            
            # Create response
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="test_result_{result.id}.csv"'
            
            return response
        except Exception as e:
            logger.error(f"Test result export error: {str(e)}")
            return Response({"detail": "Natijani eksport qilishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestResultMyResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            results = TestResult.objects.filter(user=request.user).order_by('-created_at')
            serializer = TestResultSerializer(results, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"My results error: {str(e)}")
            return Response({"detail": "Natijalarni olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)