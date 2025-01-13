from django.contrib.auth.models import AbstractUser
from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Vendor', 'Vendor'),
    ]

    full_name = models.CharField(max_length=256)
    address = models.TextField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=30, blank=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=12, blank=True, null=True, default='Customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name