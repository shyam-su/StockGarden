from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Vendor', 'Vendor'),
    ]
    full_name = models.CharField(max_length=191)
    address = models.CharField(max_length=191, blank=True, null=True)
    phone = models.IntegerField( blank=True, null=True,unique=True,db_index=True)
    email = models.EmailField(max_length=50,unique=True, blank=True)
    company_name = models.CharField(max_length=191, unique=True, blank=True, null=True)
    role = models.CharField( max_length=12,choices=ROLE_CHOICES, default='Customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        indexes = [models.Index(fields=['full_name'])]

    def __str__(self):
        return self.full_name
