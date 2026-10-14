from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('HR', 'HR'),
        ('EMPLOYEE', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    # Timestamps requested by Viraj
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return self.email

class Employee(models.Model):
    # 1:1 relationship to CustomUser as shown in the V2 diagram
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    
    employee_id = models.CharField(max_length=20, unique=True)
    job_title = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=20)
    joining_date = models.DateField()
    is_verified = models.BooleanField(default=False)
    
    # Nullable department FK (Sreelaya's design decision #1)
    department_id = models.IntegerField(null=True, blank=True) 
    
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.email}"