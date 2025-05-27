from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.core.mail import send_mail
import random
import string
from .models import CustomerUser, UserActivity, Notification
from .serializers import (
    CustomerUserSerializer, 
    ChangePasswordSerializer,
    PhoneVerificationSerializer,
    NotificationSerializer,
    CustomerUserCreateSerializer
)
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Create your views here.

class CustomerUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def post(self, request):
        """Foydalanuvchi yaratish"""
        serializer = CustomerUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': CustomerUserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"User registration error: {str(e)}")
                return Response(
                    {"detail": "Foydalanuvchi ro'yxatdan o'tkazishda xatolik yuz berdi"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        # /users/me/ yoki /users/ (profil) uchun
        if pk == 'me' or pk is None:
            user = request.user
            # Profil ko'rilishini log qilish
            ip_address = request.META.get('REMOTE_ADDR') or '127.0.0.1'
            UserActivity.objects.create(
                user=request.user,
                activity_type='profile_view',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return Response(CustomerUserSerializer(user).data)
        else:
            # Faqat staff boshqa userlarni ko'ra oladi
            if not request.user.is_staff:
                return Response(
                    {"detail": "Ruxsat yo'q"},
                    status=status.HTTP_403_FORBIDDEN
                )
            user = get_object_or_404(CustomerUser, pk=pk)
            # Profil ko'rilishini log qilish
            ip_address = request.META.get('REMOTE_ADDR') or '127.0.0.1'
            UserActivity.objects.create(
                user=request.user,
                activity_type='profile_view',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return Response(CustomerUserSerializer(user).data)

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        # /users/me/ uchun
        if pk == "me" or pk is None:
            user = request.user
        else:
            user = get_object_or_404(CustomerUser, pk=pk)
            if not (request.user.is_staff or request.user == user):
                return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CustomerUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Foydalanuvchini o'chirish"""
        pk = kwargs.get('pk')
        if not request.user.is_staff:
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
        user = get_object_or_404(CustomerUser, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"detail": "Username/email va parolni kiriting"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Login urinishlarini tekshirish
        ip_address = request.META.get('REMOTE_ADDR') or '127.0.0.1'
        login_attempts = UserActivity.objects.filter(
            ip_address=ip_address,
            activity_type='login_attempt',
            created_at__gte=timezone.now() - timezone.timedelta(minutes=15)
        ).count()
        
        if login_attempts >= 5:
            return Response(
                {"detail": "Juda ko'p marta urinish. Iltimos, 15 daqiqa kutib turing."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
            
        user = None
        user_by_username = CustomerUser.objects.filter(username=username).first()
        user_by_email = CustomerUser.objects.filter(email=username).first()
        user = user_by_username or user_by_email
        
        # Login urinishini log qilish
        UserActivity.objects.create(
            user=user,  # Agar user topilgan bo'lsa, uni log qilish
            ip_address=ip_address,
            activity_type='login_attempt',
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        if user:
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user and authenticated_user.is_active:
                # Login muvaffaqiyatli bo'ldi
                login(request, authenticated_user)
                
                # Login faoliyatini log qilish
                UserActivity.objects.create(
                    user=authenticated_user,
                    activity_type='login',
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Login vaqtini yangilash
                authenticated_user.last_login = timezone.now()
                authenticated_user.last_login_ip = ip_address
                authenticated_user.save()
                
                refresh = RefreshToken.for_user(authenticated_user)
                return Response({
                    'user': CustomerUserSerializer(authenticated_user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response(
                {"detail": "Noto'g'ri parol"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {"detail": "Bunday foydalanuvchi topilmadi"},
            status=status.HTTP_401_UNAUTHORIZED
        )

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Logout faoliyatini log qilish
            ip_address = request.META.get('REMOTE_ADDR') or '127.0.0.1'
            UserActivity.objects.create(
                user=request.user,
                activity_type='logout',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            return Response(
                {"detail": "Muvaffaqiyatli chiqildi"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "Chiqishda xatolik yuz berdi"},
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"detail": "Eski parol noto'g'ri"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Parol o'zgartirish faoliyatini log qilish
            ip_address = request.META.get('REMOTE_ADDR') or '127.0.0.1'
            UserActivity.objects.create(
                user=user,
                activity_type='password_change',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response(
                {"detail": "Parol muvaffaqiyatli o'zgartirildi"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        if user.is_email_verified:
            return Response({"message": "Email allaqachon tasdiqlangan"})
        
        # Generate verification token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        user.email_verification_token = token
        user.save()
        
        # Send verification email
        verification_url = f"http://yourdomain.com/verify-email/{token}"
        send_mail(
            'Email tasdiqlash',
            f'Emailingizni tasdiqlash uchun quyidagi havolani bosing: {verification_url}',
            'from@yourdomain.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response({"message": "Tasdiqlash emaili yuborildi"})

class VerifyPhoneView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PhoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Here you would implement SMS verification logic
        # For now, we'll just return a success message
        return Response({"message": "Telefon raqam tasdiqlandi"})

class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        notification_id = request.data.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Xabar o'qildi deb belgilandi"})
        except Notification.DoesNotExist:
            return Response({"error": "Xabar topilmadi"}, status=status.HTTP_404_NOT_FOUND)
