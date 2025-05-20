from django.db import models
from Base.models import BaseModel
from CustomerUser.models import CustomerUser
from Course.models import Module

class Test(BaseModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='tests')
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    time_limit = models.DurationField()
    passing_score = models.IntegerField()
    attempt_limit = models.IntegerField(default=1)
    is_final_test = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'

class QuestionTypes(models.TextChoices):
    SINGLE = 'single_choice', 'Single Choice'
    MULTIPLE = 'multiple_choice', 'Multiple Choice'
    TEXT = 'text', 'Text'

class Question(BaseModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QuestionTypes.choices)
    options = models.JSONField()
    correct_answer = models.JSONField()

    def __str__(self):
        return f"{self.test.title} - {self.question_text[:50]}"

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
