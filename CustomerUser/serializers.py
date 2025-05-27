from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomerUser, UserActivity, Notification

class CustomerUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ], required=False)
    phone_number = serializers.CharField(max_length=15, required=False, allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return CustomerUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CustomerUserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ], required=False)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi"})
        
        # Email yoki phone_numberdan faqat bittasi bo'lishi kerak
        if data.get('email') and data.get('phone_number'):
            raise serializers.ValidationError("Faqat bitta: email yoki phone_number bo'lishi shart!")
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError("Email yoki phone_number kiritilishi shart!")
            
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

class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=Notification.Types.choices)
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    is_read = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all())
    activity_type = serializers.CharField(max_length=50)
    ip_address = serializers.CharField(required=False, allow_null=True)
    user_agent = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return UserActivity.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance