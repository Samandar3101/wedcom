from django.db import models
from django.contrib.auth.models import AbstractUser
from Base.models import BaseModel

class CustomerUser(AbstractUser, BaseModel):
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ])
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None or not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
