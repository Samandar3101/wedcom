from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Test, Question, Answer, TestResult
from Course.models import Course, Category
from CustomerUser.models import CustomerUser
from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone

class TestModelTests(TestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
            course=self.course,
            title='Test Test',
            description='Test Description',
            duration_minutes=30,
            passing_score=70
        )

    def test_test_creation(self):
        """Test yaratishni tekshirish"""
        self.assertEqual(self.test.course, self.course)
        self.assertEqual(self.test.title, 'Test Test')
        self.assertEqual(self.test.passing_score, 70)
        self.assertTrue(self.test.is_active)

    def test_test_string_representation(self):
        """Test string ko'rinishini tekshirish"""
        self.assertEqual(str(self.test), 'Test Test')

class QuestionModelTests(TestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
            course=self.course,
            title='Test Test',
            description='Test Description',
            duration_minutes=30,
            passing_score=70
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            points=1,
            order=1
        )

    def test_question_creation(self):
        """Savol yaratishni tekshirish"""
        self.assertEqual(self.question.test, self.test)
        self.assertEqual(self.question.text, 'Test Question')
        self.assertEqual(self.question.points, 1)
        self.assertEqual(self.question.order, 1)

    def test_question_string_representation(self):
        """Savol string ko'rinishini tekshirish"""
        self.assertEqual(str(self.question), 'Test Test - Question 1')

class AnswerModelTests(TestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
            course=self.course,
            title='Test Test',
            description='Test Description',
            duration_minutes=30,
            passing_score=70
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            points=1,
            order=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            is_correct=True
        )

    def test_answer_creation(self):
        """Javob yaratishni tekshirish"""
        self.assertEqual(self.answer.question, self.question)
        self.assertEqual(self.answer.text, 'Test Answer')
        self.assertTrue(self.answer.is_correct)

    def test_answer_string_representation(self):
        """Javob string ko'rinishini tekshirish"""
        self.assertEqual(str(self.answer), 'Test Question - Test Answer')

class TestAPITests(APITestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='teacher'
        )
        self.admin_user = CustomerUser.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123'
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
        self.test1 = Test.objects.create(
            course=self.course,
            title='Test 1',
            description='Test Description 1',
            duration_minutes=30,
            passing_score=70
        )
        self.test2 = Test.objects.create(
            course=self.course,
            title='Test 2',
            description='Test Description 2',
            duration_minutes=30,
            passing_score=80
        )
        self.test3 = Test.objects.create(
            course=self.course,
            title='Test 3',
            description='Test Description 3',
            duration_minutes=30,
            passing_score=90
        )
        self.client.force_authenticate(user=self.user)

    def test_create_test(self):
        """Test yaratishni tekshirish"""
        url = reverse('test-list')
        data = {
            'course_id': str(self.course.id),
            'title': 'New Test',
            'description': 'New Test Description',
            'duration_minutes': 30,
            'passing_score': 75
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Test.objects.count(), 4)

    def test_list_tests(self):
        """Testlar ro'yxatini tekshirish"""
        url = reverse('test-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_retrieve_test(self):
        """Test ma'lumotlarini olishni tekshirish"""
        url = reverse('test-detail', args=[self.test1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test 1')

    def test_update_test(self):
        """Test ma'lumotlarini yangilashni tekshirish"""
        url = reverse('test-detail', args=[self.test1.id])
        data = {
            'course_id': str(self.course.id),
            'title': 'Updated Test',
            'description': 'Updated Description',
            'duration_minutes': 45,
            'passing_score': 80
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test1.refresh_from_db()
        self.assertEqual(self.test1.title, 'Updated Test')

    def test_delete_test(self):
        """Testni o'chirishni tekshirish"""
        url = reverse('test-detail', args=[self.test1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Test.objects.count(), 2)

    def test_test_ordering(self):
        """Testlarni tartiblashni tekshirish"""
        url = reverse('test-list') + '?ordering=title'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Test 1')
        self.assertEqual(response.data[1]['title'], 'Test 2')
        self.assertEqual(response.data[2]['title'], 'Test 3')

    def test_test_filtering(self):
        """Testlarni filtrlashni tekshirish"""
        url = reverse('test-list') + '?course=' + str(self.course.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_unauthorized_access(self):
        """Ruxsatsiz kirishni tekshirish"""
        self.client.force_authenticate(user=None)
        url = reverse('test-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class QuestionAPITests(APITestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='teacher'
        )
        self.admin_user = CustomerUser.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123'
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
            course=self.course,
            title='Test Test',
            description='Test Description',
            duration_minutes=30,
            passing_score=70
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            points=1,
            order=1
        )
        self.client.force_authenticate(user=self.user)

    def test_create_question(self):
        """Savol yaratishni tekshirish"""
        url = reverse('question-list')
        data = {
            'test_id': str(self.test.id),
            'text': 'New Question',
            'points': 2,
            'order': 2,
            'answers': [
                {'text': 'A', 'is_correct': True},
                {'text': 'B', 'is_correct': False}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)

    def test_list_questions(self):
        """Savollar ro'yxatini tekshirish"""
        url = reverse('question-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_question(self):
        """Savol ma'lumotlarini olishni tekshirish"""
        url = reverse('question-detail', args=[self.question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test Question')

    def test_update_question(self):
        """Savol ma'lumotlarini yangilashni tekshirish"""
        url = reverse('question-detail', args=[self.question.id])
        data = {
            'test_id': str(self.test.id),
            'text': 'Updated Question',
            'points': 2,
            'order': 1,
            'answers': [
                {'text': 'A', 'is_correct': True},
                {'text': 'B', 'is_correct': False}
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, 'Updated Question')

    def test_delete_question(self):
        """Savolni o'chirishni tekshirish"""
        url = reverse('question-detail', args=[self.question.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 0)

    def test_question_ordering(self):
        """Savollarni tartiblashni tekshirish"""
        Question.objects.create(
            test=self.test,
            text='Second Question',
            points=1,
            order=2
        )
        url = reverse('question-list') + '?ordering=order'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['text'], 'Test Question')
        self.assertEqual(response.data[1]['text'], 'Second Question')

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
            price=100,
            category=self.category,
            instructor=self.user,
            duration=timedelta(hours=2)
        )
        self.test = Test.objects.create(
            course=self.course,
            title='Test Test',
            description='Test Description',
            duration_minutes=30,
            passing_score=70
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question',
            points=1,
            order=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            is_correct=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_result(self):
        """Test natijasini yaratishni tekshirish"""
        url = reverse('testresult-list')
        data = {
            'test_id': str(self.test.id),
            'user_id': str(self.user.id),
            'score': 100,
            'completed_at': timezone.now().isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestResult.objects.count(), 1)

    def test_list_results(self):
        """Test natijalari ro'yxatini tekshirish"""
        TestResult.objects.create(
            test=self.test,
            user=self.user,
            score=100,
            completed_at=timezone.now()
        )
        url = reverse('testresult-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_result(self):
        """Test natijasini olishni tekshirish"""
        result = TestResult.objects.create(
            test=self.test,
            user=self.user,
            score=100,
            completed_at=timezone.now()
        )
        url = reverse('testresult-detail', args=[result.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['score']), 100.0)

    def test_result_calculation(self):
        """Test natijasini hisoblashni tekshirish"""
        result = TestResult.objects.create(
            test=self.test,
            user=self.user,
            answers={str(self.question.id): str(self.answer.id)},
            completed_at=timezone.now()
        )
        result.save()  # This will trigger score calculation
        self.assertEqual(result.score, 100)
        self.assertTrue(result.passed)