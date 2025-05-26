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
    LoginSerializer,
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

logger = logging.getLogger(__name__)

# Create your views here.

class CustomerUserViewSet(viewsets.ModelViewSet):
    queryset = CustomerUser.objects.all()
    serializer_class = CustomerUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='login',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Update last login IP
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save()
            
            return Response(CustomerUserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"error": "Eski parol noto'g'ri"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='password_change',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({"message": "Parol muvaffaqiyatli o'zgartirildi"})

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
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

    @action(detail=False, methods=['post'])
    def verify_phone(self, request):
        serializer = PhoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Here you would implement SMS verification logic
        # For now, we'll just return a success message
        return Response({"message": "Telefon raqam tasdiqlandi"})

    @action(detail=False, methods=['get'])
    def notifications(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_notification_read(self, request):
        notification_id = request.data.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Xabar o'qildi deb belgilandi"})
        except Notification.DoesNotExist:
            return Response({"error": "Xabar topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        user = serializer.save()
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='registration',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def get_object(self):
        pk = self.kwargs.get('pk')
        if pk == "me":
            return self.request.user
        return super().get_object()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
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
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')  # username yoki email bo'lishi mumkin
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"detail": "Username/email va parolni kiriting"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Username yoki email orqali foydalanuvchini qidirish
        user = None
        user_by_username = CustomerUser.objects.filter(username=username).first()
        user_by_email = CustomerUser.objects.filter(email=username).first()
        user = user_by_username or user_by_email
        
        if user:
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user and authenticated_user.is_active:
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

class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        users = CustomerUser.objects.all()
        serializer = CustomerUserSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(CustomerUser, pk=pk)
    
    def get(self, request, pk):
        user = self.get_object(pk)
        if not (request.user.is_staff or request.user == user):
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = CustomerUserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, pk):
        user = self.get_object(pk)
        if not (request.user.is_staff or request.user == user):
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = CustomerUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                logger.error(f"User update error: {str(e)}")
                return Response(
                    {"detail": "Foydalanuvchi ma'lumotlarini yangilashda xatolik yuz berdi"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = self.get_object(pk)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"User deletion error: {str(e)}")
            return Response(
                {"detail": "Foydalanuvchini o'chirishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = CustomerUserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = CustomerUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                logger.error(f"Profile update error: {str(e)}")
                return Response(
                    {"detail": "Profil ma'lumotlarini yangilashda xatolik yuz berdi"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
