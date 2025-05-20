from django.db import models
from Base.models import BaseModel
from CustomerUser.models import CustomerUser

class Category(BaseModel):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='categories/', null=True, blank=True)

    class Meta:
        verbose_name = 'Category'   
        verbose_name_plural = 'Categories'

class Course(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='instructor_courses')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_free = models.BooleanField(default=False)
    duration = models.DurationField()
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], null=True, blank=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

class Lesson(BaseModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    duration = models.DurationField()
    order = models.PositiveIntegerField()
    

    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        
class Progress(BaseModel):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completion_date = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Progress'
        verbose_name_plural = 'Progress'

class Review(BaseModel):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews' 