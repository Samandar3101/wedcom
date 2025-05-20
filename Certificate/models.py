from django.db import models
from Base.models import BaseModel
from CustomerUser.models import CustomerUser
from Course.models import Course
import uuid

class Certificate(BaseModel):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_code = models.CharField(max_length=100, unique=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.certificate_code:
            # Sertifikat uchun unikal kod (10 belgili UUID qisqargan)
            self.certificate_code = str(uuid.uuid4()).replace('-', '').upper()[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title} Certificate"

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        unique_together = ('user', 'course')  # Har bir foydalanuvchiga bitta kursdan 1ta sertifikat
