from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomerUser, UserActivity, Notification

class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active', 'is_staff', 'date_joined', 'last_login', 'last_login_ip']
        read_only_fields = ['id', 'date_joined', 'last_login', 'last_login_ip']

class CustomerUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomerUser
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'role']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi"})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomerUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)  # Bu maydon username yoki email bo'lishi mumkin
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        login_input = data.get('username')
        password = data.get('password')

        # Username yoki email orqali foydalanuvchini qidirish
        user = None
        if login_input:
            # Avval username bo'yicha qidiramiz
            user_by_username = CustomerUser.objects.filter(username=login_input).first()
            # Agar username bo'yicha topilmasa, email bo'yicha qidiramiz
            user_by_email = CustomerUser.objects.filter(email=login_input).first()
            # Ikkalasidan birini tanlaymiz
            user = user_by_username or user_by_email

        if user:
            # Django autentifikatsiyasidan foydalanamiz
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user and authenticated_user.is_active:
                return authenticated_user
            raise serializers.ValidationError("Parol noto'g'ri.")
        raise serializers.ValidationError("Bunday username yoki email mavjud emas.")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

def validate(self, data):
     if data['new_password'] != data['confirm_password']:
        raise serializers.ValidationError("New passwords do not match")
     return data

class PhoneVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    verification_code = serializers.CharField(required=True)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'is_read', 'created_at']

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'activity_type', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']