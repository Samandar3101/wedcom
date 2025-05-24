from django.db import models
from Base.models import BaseModel
from CustomerUser.models import CustomerUser
from Course.models import Course

class Test(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tests')
    duration_minutes = models.IntegerField()
    passing_score = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, related_name='created_tests')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'

class Question(BaseModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    points = models.IntegerField(default=1)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.test.title} - Question {self.order}"

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order']

class Answer(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:50]} - {self.text[:50]}"

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

class TestResult(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='test_results')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test.title} - {self.user.email}"

    def save(self, *args, **kwargs):
        if self.completed_at and not self.score:
            # Calculate score when test is completed
            total_questions = self.test.questions.count()
            if total_questions > 0:
                correct_answers = sum(1 for q_id, a_id in self.answers.items() 
                                   if Answer.objects.get(id=a_id).is_correct)
                self.score = (correct_answers / total_questions) * 100
                self.passed = self.score >= self.test.passing_score
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['test', 'user']