from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Removed first_name, last_name, date_joined, and username
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default='Employee')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Set to empty list as requested

    def __str__(self):
        return self.email

class Employee(models.Model):
    # Added user_id foreign key (OneToOne is best practice here) and removed department_id[cite: 13]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    def __str__(self):
        return f"Employee Profile: {self.user.email}"