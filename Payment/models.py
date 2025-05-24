from django.db import models
from Base.models import BaseModel
from CustomerUser.models import CustomerUser
from Course.models import Course
import uuid
from django.utils import timezone

class Payment(BaseModel):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('payme', 'Payme'),
        ('click', 'Click'),
        ('cash', 'Cash'),
    ]

    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_provider_id = models.CharField(max_length=100, blank=True, null=True)
    payment_provider_data = models.JSONField(default=dict, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.course.title} - {self.amount} so'm"

    def refund(self, amount=None, reason=""):
        if self.status != 'completed':
            raise ValueError("Only completed payments can be refunded")
        
        if amount is None:
            amount = self.amount
        
        if amount > self.amount:
            raise ValueError("Refund amount cannot be greater than payment amount")
        
        self.status = 'refunded'
        self.refund_amount = amount
        self.refund_date = timezone.now()
        self.refund_reason = reason
        self.save()

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']
