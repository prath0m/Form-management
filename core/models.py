from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_authorized = models.BooleanField(default=False)  # Tracks if admin is approved
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')],
        default='pending'
    )
        
class FormUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, null=True)
    file_type = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.file.name} - {self.status}"

class PreviousFinding(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # FIXED HERE ✅
    finding_number = models.IntegerField()  # 1-7 to identify fields
    finding_text = models.TextField()

    def __str__(self):
        return f"Finding {self.finding_number} - {self.user.username}"
    
    
class FormSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    form_type = models.CharField(max_length=50, blank=True, null=True)
    submitted_file = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.form_type} at {self.submitted_at}"
