from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

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

    def __str__(self):
        return f"{self.file.name} - {self.status}"