from django.contrib import admin
from .models import Course, Category, Module, Lesson, Progress, Review

admin.site.register(Course)
admin.site.register(Category)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Progress)
admin.site.register(Review)