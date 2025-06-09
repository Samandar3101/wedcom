from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomerUser, Notification, UserActivity

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
        self.register_url = reverse('user-list')
        self.login_url = reverse('login')
        self.user_data = {
            'username': f'testuser_{self._testMethodName}',
            'email': f'test_{self._testMethodName}@example.com',
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
        self.assertEqual(CustomerUser.objects.get().username, self.user_data['username'])

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
            username=self.user_data['username'],
            email=self.user_data['email'],
            password='testpass123'
        )
        
        # Xuddi shu username bilan qayta ro'yxatdan o'tishga harakat qilamiz
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile(self):
        """Test foydalanuvchi profilini yangilash"""
        # Avval foydalanuvchini yaratamiz va tizimga kiritamiz
        user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Profilni yangilash
        update_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number': '+998901234567'
        }
        response = self.client.put('/users/me/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertEqual(response.data['phone_number'], '+998901234567')

    def test_get_user_profile(self):
        """Test foydalanuvchi profilini olish"""
        # Avval foydalanuvchini yaratamiz va tizimga kiritamiz
        user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Profilni olish
        response = self.client.get('/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_mark_notification_read(self):
        """Test xabarni o'qilgan deb belgilash"""
        # Avval foydalanuvchini yaratamiz va tizimga kiritamiz
        user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Xabar yaratamiz
        notification = Notification.objects.create(
            user=user,
            type='info',
            title='Test Notification',
            message='This is a test notification'
        )
        
        # Xabarni o'qilgan deb belgilash
        response = self.client.post('/notifications/mark-read/', 
                                  {'notification_id': notification.id}, 
                                  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Xabarning holatini tekshiramiz
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_verify_email(self):
        """Test email tasdiqlash"""
        # Avval foydalanuvchini yaratamiz va tizimga kiritamiz
        user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Email tasdiqlash so'rovini yuboramiz
        response = self.client.post('/verify-email/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_verify_phone(self):
        """Test telefon raqam tasdiqlash"""
        # Avval foydalanuvchini yaratamiz va tizimga kiritamiz
        user = CustomerUser.objects.create_user(
            username='testuser',
            phone_number='+998901234567',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Telefon raqam tasdiqlash so'rovini yuboramiz
        verification_data = {
            'phone_number': '+998901234567',
            'verification_code': '123456'
        }
        response = self.client.post('/verify-phone/', verification_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_user_activity(self):
        """Test foydalanuvchi faoliyatini kuzatish"""
        # Avval foydalanuvchini yaratamiz va tizimga kiritamiz
        user = CustomerUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Bir nechta amallarni bajaramiz
        self.client.get('/users/me/')  # Profilni olish
        self.client.post('/logout/')  # Tizimdan chiqish
        
        # Faoliyatlarni tekshiramiz
        activities = UserActivity.objects.filter(user=user).order_by('created_at')
        self.assertEqual(activities.count(), 2)  # 2 ta faoliyat: profil olish va chiqish
        self.assertEqual(activities[0].activity_type, 'profile_view')
        self.assertEqual(activities[1].activity_type, 'logout')
