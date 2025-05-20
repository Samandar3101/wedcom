from django.db import models
from Base.models import BaseModel
from CustomerUser.models import CustomerUser
from Course.models import Course
import uuid

class Payment(BaseModel):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4()).replace('-', '').upper()[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.course.title} - {self.amount} so'm"

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
