from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Vendor', 'Vendor'),
    ]
    full_name = models.CharField(max_length=191)
    address = models.TextField(max_length=191, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True)
    role = models.CharField( max_length=12,choices=ROLE_CHOICES, default='Customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
