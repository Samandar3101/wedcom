from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Test, Question, Answer, TestResult
from CustomerUser.models import CustomerUser
from Course.models import Course, Category
from datetime import timedelta
from django.utils import timezone

class TestModelTests(TestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='teacher'
        )
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.test = Test.objects.create(
            title='Test Title',
            description='Test Description',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )

    def test_test_creation(self):
        self.assertEqual(self.test.title, 'Test Title')
        self.assertEqual(self.test.course, self.course)
        self.assertEqual(self.test.created_by, self.user)
        self.assertTrue(self.test.is_active)

    def test_test_str(self):
        self.assertEqual(str(self.test), 'Test Title')

class QuestionModelTests(TestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='teacher'
        )
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.test = Test.objects.create(
            title='Test Title',
            description='Test Description',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            order=1
        )

    def test_question_creation(self):
        self.assertEqual(self.question.text, 'Test Question')
        self.assertEqual(self.question.test, self.test)
        self.assertEqual(self.question.order, 1)

    def test_question_str(self):
        self.assertEqual(str(self.question), f'{self.test.title} - Question {self.question.order}')

class AnswerModelTests(TestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='teacher'
        )
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.test = Test.objects.create(
            title='Test Title',
            description='Test Description',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            order=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            is_correct=True
        )

    def test_answer_creation(self):
        self.assertEqual(self.answer.text, 'Test Answer')
        self.assertEqual(self.answer.question, self.question)
        self.assertTrue(self.answer.is_correct)

    def test_answer_str(self):
        self.assertEqual(str(self.answer), f'{self.question.text} - {self.answer.text}')

class TestResultModelTests(TestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student'
        )
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100,
            category=self.category,
            instructor=self.user,
            duration=timedelta(hours=2)
        )
        self.test = Test.objects.create(
            title='Test Title',
            description='Test Description',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            order=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            is_correct=True
        )
        self.result = TestResult.objects.create(
            test=self.test,
            user=self.user,
            score=80,
            passed=True,
            started_at=timezone.now(),
            completed_at=timezone.now() + timedelta(minutes=20),
            answers={str(self.question.id): str(self.answer.id)}
        )

    def test_result_creation(self):
        self.assertEqual(self.result.test, self.test)
        self.assertEqual(self.result.user, self.user)
        self.assertEqual(self.result.score, 80)
        self.assertTrue(self.result.passed)

    def test_result_str(self):
        self.assertEqual(str(self.result), f'Test Title - test@example.com')

class TestAPITests(APITestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='teacher'
        )
        self.admin_user = CustomerUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        self.student_user = CustomerUser.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123',
            role='student'
        )
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.test = Test.objects.create(
            title='Test Title',
            description='Test Description',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_create_test(self):
        url = reverse('test-list')
        data = {
            'title': 'New Test',
            'description': 'New Description',
            'course': self.course.id,
            'duration_minutes': 45,
            'passing_score': 75
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Test.objects.count(), 2)
        self.assertEqual(Test.objects.get(title='New Test').created_by, self.user)

    def test_list_tests_teacher(self):
        url = reverse('test-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All tests including inactive ones

    def test_list_tests_student(self):
        self.client.force_authenticate(user=self.student_user)
        url = reverse('test-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All active tests

    def test_retrieve_test(self):
        url = reverse('test-detail', args=[self.test.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Title')

    def test_update_test(self):
        url = reverse('test-detail', args=[self.test.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Test.objects.get(id=self.test.id).title, 'Updated Title')

    def test_delete_test(self):
        url = reverse('test-detail', args=[self.test.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Test.objects.count(), 0)

    def test_test_ordering(self):
        # Create multiple tests
        Test.objects.create(
            title='Test 1',
            description='Description 1',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )
        Test.objects.create(
            title='Test 2',
            description='Description 2',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )

        # Test ordering by created_at
        url = reverse('test-list')
        response = self.client.get(url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['title'], 'Test 2')

        # Test ordering by title
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Test 1')

    def test_test_filtering(self):
        # Create test with different parameters
        Test.objects.create(
            title='Filtered Test',
            description='Description',
            course=self.course,
            duration_minutes=60,
            passing_score=80,
            created_by=self.user
        )

        # Test filtering by duration
        url = reverse('test-list')
        response = self.client.get(url, {'min_duration': 45})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Filtered Test')

        # Test filtering by passing score
        response = self.client.get(url, {'min_passing_score': 75})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Filtered Test')

class QuestionAPITests(APITestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='teacher'
        )
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.test = Test.objects.create(
            title='Test Title',
            description='Test Description',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            order=1
        )
        self.client.force_authenticate(user=self.user)

    def test_create_question(self):
        url = reverse('question-list')
        data = {
            'test': self.test.id,
            'text': 'New Question',
            'order': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_questions(self):
        url = reverse('question-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All questions

    def test_retrieve_question(self):
        url = reverse('question-detail', args=[self.question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test Question')

class TestResultAPITests(APITestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student'
        )
        self.category = Category.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.test = Test.objects.create(
            title='Test Title',
            description='Test Description',
            course=self.course,
            duration_minutes=30,
            passing_score=70,
            created_by=self.user
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            order=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            is_correct=True
        )
        self.result = TestResult.objects.create(
            test=self.test,
            user=self.user,
            score=80,
            passed=True,
            started_at=timezone.now(),
            completed_at=timezone.now() + timedelta(minutes=20),
            answers={str(self.question.id): str(self.answer.id)}
        )
        self.client.force_authenticate(user=self.user)

    def test_create_result(self):
        url = reverse('testresult-list')
        data = {
            'test': self.test.id,
            'answers': {
                str(self.question.id): str(self.answer.id)
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestResult.objects.count(), 2)

    def test_list_results(self):
        url = reverse('testresult-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All results

    def test_retrieve_result(self):
        url = reverse('testresult-detail', args=[self.result.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 80)

    def test_my_results(self):
        url = reverse('testresult-my-results')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only user's results

    def test_export_result(self):
        url = reverse('testresult-export-result', args=[self.result.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
