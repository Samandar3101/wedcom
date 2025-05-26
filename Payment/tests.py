from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Payment
from CustomerUser.models import CustomerUser
from Course.models import Course, Category
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from unittest.mock import patch

# Add required payment settings
settings.PAYME_MERCHANT_ID = 'test_merchant_id'
settings.PAYME_SECRET_KEY = 'test_secret_key'
settings.PAYME_CALLBACK_URL = 'http://localhost:8000/api/payments/callback/'
settings.PAYME_API_URL = 'https://test.paycom.uz/api/'

class PaymentModelTests(TestCase):
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
        self.payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=100,
            method='payme',
            status='pending'
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.course, self.course)
        self.assertEqual(self.payment.amount, Decimal('100'))
        self.assertEqual(self.payment.status, 'pending')
        self.assertEqual(self.payment.method, 'payme')

    def test_payment_str(self):
        self.assertEqual(str(self.payment), f'{self.user.email} - {self.course.title} - {self.payment.amount} so\'m')

class PaymentAPITests(APITestCase):
    def setUp(self):
        self.user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=100000,
            status='pending',
            method='payme'
        )
        self.client.force_authenticate(user=self.user)

    @patch('Payment.providers.PaymeProvider.create_payment')
    def test_create_payment(self, mock_create_payment):
        mock_create_payment.return_value = {
            'provider_id': 'test_id',
            'checkout_url': 'http://test.com',
            'provider_data': {}
        }
        url = reverse('payment-list')
        data = {
            'course': self.course.id,
            'method': 'payme'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 2)

    def test_list_payments(self):
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_payment(self):
        url = reverse('payment-detail', args=[self.payment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '100000.00')

    def test_update_payment(self):
        url = reverse('payment-detail', args=[self.payment.id])
        data = {
            'payment_provider_id': 'new_provider_id',
            'payment_provider_data': {'test': 'data'}
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_provider_id'], 'new_provider_id')

    def test_refund_payment(self):
        # First complete the payment
        self.payment.status = 'completed'
        self.payment.payment_date = timezone.now()
        self.payment.save()

        url = reverse('payment-refund', args=[self.payment.id])
        data = {
            'amount': 100000,
            'reason': 'Test refund reason with more than 10 characters'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'refunded')

    def test_cancel_payment(self):
        url = reverse('payment-cancel', args=[self.payment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')

    def test_webhook(self):
        self.payment.payment_provider_id = 'test_id'
        self.payment.save()
        url = reverse('payment-webhook', args=['payme'])
        data = {
            'payment_id': 'test_id',
            'status': 'completed'
        }
        headers = {'X-Signature': 'test_signature'}
        with patch('Payment.providers.PaymeProvider.verify_webhook', return_value=True), \
             patch('Payment.providers.PaymeProvider.check_payment_status', return_value='completed'):
            response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refund_time_limit(self):
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=100000,
            status='completed',
            method='payme',
            payment_date=timezone.now() - timedelta(days=31)  # 31 days ago
        )

        url = reverse('payment-refund', args=[payment.id])
        data = {
            'amount': 100000,
            'reason': 'Test refund reason with more than 10 characters'
        }
        with patch('Payment.providers.PaymeProvider.process_refund', return_value=False):
            response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("To'lovdan keyin 30 kundan o'tgan bo'lsa, qaytarish mumkin emas", str(response.data))

class PaymentValidationTests(APITestCase):
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
            price=100000,
            duration=timedelta(hours=2),
            category=self.category,
            instructor=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_invalid_payment_method(self):
        url = reverse('payment-list')
        data = {
            'course': self.course.id,
            'method': 'invalid_method'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('"invalid_method" is not a valid choice', str(response.data))

    def test_cash_payment_limit(self):
        self.course.price = 2000000  # 2 million
        self.course.save()

        url = reverse('payment-list')
        data = {
            'course': self.course.id,
            'method': 'cash'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Naqd pul orqali to'lov 1 million so'mdan oshmasligi kerak", str(response.data))

    def test_refund_validation(self):
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=100000,
            status='completed',
            method='payme',
            payment_date=timezone.now()
        )

        url = reverse('payment-refund', args=[payment.id])
        data = {
            'amount': 200000,  # More than payment amount
            'reason': 'Test refund reason with more than 10 characters'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refund_reason_length(self):
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=100000,
            status='completed',
            method='payme',
            payment_date=timezone.now()
        )

        url = reverse('payment-refund', args=[payment.id])
        data = {
            'amount': 100000,
            'reason': 'Too short'  # Less than 10 characters
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Qaytarish sababi kamida 10 ta belgidan iborat bo\'lishi kerak', str(response.data))