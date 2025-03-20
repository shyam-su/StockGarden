from django.contrib import admin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display =('full_name','address','phone','email','company_name','role','is_active','created_at','updated_at',)
    list_filter = ('role','created_at')

