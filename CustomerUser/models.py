from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from Base.models import BaseModel

class CustomerUserManager(BaseUserManager):
    def create_user(self, username, email=None, phone_number=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username kiritilishi shart')
        # Agar createsuperuser ishlatilayotgan bo'lsa, email/phone validatsiyasini o'tkazib yuboramiz
        if 'is_superuser' in extra_fields and extra_fields['is_superuser']:
            email = self.normalize_email(email) if email else None
            user = self.model(username=username, email=email, phone_number=phone_number, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        # Oddiy foydalanuvchi uchun email yoki phone_numberdan faqat bittasi bo'lishi shart
        if (email and phone_number) or (not email and not phone_number):
            raise ValueError('Faqat bitta: email yoki phone_number bo\'lishi shart!')
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, email=None, phone_number=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, phone_number, password, **extra_fields)

    def get_by_natural_key(self, username):
        # Username yoki email bo'yicha qidirish
        user_by_username = self.filter(username=username).first()
        user_by_email = self.filter(email=username).first()
        user = user_by_username or user_by_email
        if user:
            return user
        raise self.model.DoesNotExist("Foydalanuvchi topilmadi.")

class CustomerUser(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ])
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomerUserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser or self.is_staff

    def has_module_perms(self, app_label):
        return self.is_superuser or self.is_staff

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class UserActivity(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)  # login, logout, password_change, etc.
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'

class Notification(models.Model):
    class Types(models.TextChoices):
        TEST_RESULT = 'test_result', 'Test Result'
        PAYMENT = 'payment', 'Payment'
        SYSTEM = 'system', 'System'

    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=Types.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'