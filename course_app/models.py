from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User


# models.py
from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Group(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    start_date = models.DateField()

class Student(models.Model):
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='students')

    def __str__(self):
        return self.name


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    day_number = models.IntegerField(null=True, blank=True)  # 1-18
    value = models.CharField(max_length=1, blank=True)
