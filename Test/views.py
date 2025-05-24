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

class TestCreateAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        test = get_object_or_404(Test, pk=pk)
        serializer = TestSerializer(test)
        return Response(serializer.data)

class TestUpdateAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def put(self, request, pk):
        test = get_object_or_404(Test, pk=pk)
        serializer = TestSerializer(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestDeleteAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def delete(self, request, pk):
        test = get_object_or_404(Test, pk=pk)
        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# === QUESTION ===
class QuestionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Question.objects.all()
            test_id = request.query_params.get('test')
            if test_id:
                queryset = queryset.filter(test_id=test_id)
            serializer = QuestionSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Question list error: {str(e)}")
            return Response({"detail": "Savollarni olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionCreateAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def post(self, request):
        serializer = QuestionCreateSerializer(data=request.data)
        if serializer.is_valid():
            test = get_object_or_404(Test, pk=request.data.get('test'))
            if test.course.instructor != request.user and not request.user.is_admin:
                return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

class QuestionUpdateAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def put(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        if question.test.course.instructor != request.user and not request.user.is_admin:
            return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)
        serializer = QuestionCreateSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDeleteAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def delete(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        if question.test.course.instructor != request.user and not request.user.is_admin:
            return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            if request.user.is_admin:
                queryset = TestResult.objects.all()
            elif request.user.role == 'teacher':
                queryset = TestResult.objects.filter(test__course__instructor=request.user)
            else:
                queryset = TestResult.objects.filter(user=request.user)
            serializer = TestResultSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Test result list error: {str(e)}")
            return Response({"detail": "Natijalarni olishda xato"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestResultCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TestResultSerializer(data=request.data)
        if serializer.is_valid():
            test = get_object_or_404(Test, pk=request.data.get('test'))
            if test.course.students.filter(id=request.user.id).exists() or request.user.is_admin:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestResultDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        result = get_object_or_404(TestResult, pk=pk)
        if result.user != request.user and not request.user.is_admin and result.test.course.instructor != request.user:
            return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)
        serializer = TestResultSerializer(result)
        return Response(serializer.data)

class TestResultUpdateAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def put(self, request, pk):
        result = get_object_or_404(TestResult, pk=pk)
        serializer = TestResultSerializer(result, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestResultDeleteAPIView(APIView):
    permission_classes = [IsCourseInstructorOrAdmin]

    def delete(self, request, pk):
        result = get_object_or_404(TestResult, pk=pk)
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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