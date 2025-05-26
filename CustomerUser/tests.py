from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomerUser

class CustomerUserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student'
        }

    def test_create_user_with_email(self):
        """Test email bilan foydalanuvchi yaratish"""
        user = CustomerUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, self.user_data['role'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_phone(self):
        """Test telefon raqam bilan foydalanuvchi yaratish"""
        phone_user_data = {
            'username': 'phoneuser',
            'phone_number': '+998901234567',
            'password': 'testpass123',
            'first_name': 'Phone',
            'last_name': 'User',
            'role': 'student'
        }
        user = CustomerUser.objects.create_user(**phone_user_data)
        self.assertEqual(user.username, phone_user_data['username'])
        self.assertEqual(user.phone_number, phone_user_data['phone_number'])
        self.assertEqual(user.role, phone_user_data['role'])
        self.assertTrue(user.check_password(phone_user_data['password']))

    def test_create_superuser(self):
        """Test admin foydalanuvchi yaratish"""
        superuser = CustomerUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

class CustomerUserAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student'
        }

    def test_register_user_with_email(self):
        """Test email bilan ro'yxatdan o'tish"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomerUser.objects.count(), 1)
        self.assertEqual(CustomerUser.objects.get().username, 'testuser')

    def test_register_user_with_phone(self):
        """Test telefon raqam bilan ro'yxatdan o'tish"""
        phone_user_data = {
            'username': 'phoneuser',
            'phone_number': '+998901234567',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Phone',
            'last_name': 'User',
            'role': 'student'
        }
        response = self.client.post(self.register_url, phone_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomerUser.objects.count(), 1)
        self.assertEqual(CustomerUser.objects.get().username, 'phoneuser')

    def test_login_user_with_email(self):
        """Test email bilan tizimga kirish"""
        # Avval foydalanuvchini yaratamiz
        CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'test@example.com',  # Email orqali kirish
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_user_with_username(self):
        """Test username bilan tizimga kirish"""
        CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',  # Username orqali kirish
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_wrong_password(self):
        """Test noto'g'ri parol bilan kirish"""
        CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_with_existing_username(self):
        """Test mavjud username bilan ro'yxatdan o'tish"""
        # Avval foydalanuvchini yaratamiz
        CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Xuddi shu username bilan qayta ro'yxatdan o'tishga harakat qilamiz
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
