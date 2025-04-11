from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


import re

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name','address','phone','email','company_name','role','is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Full Name','id':'full_name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address','id':'address'}),
            'phone': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone','id':'phone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email','id':'email'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Company Name','id':'company_name'}),
            'role': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Role','id':'role'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'is_active'}),  
        }
        labels = {
            'full_name': 'Full Name',
            'address': 'Address',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'company_name': 'Enter Company Name',
            'role': 'Role',
            'is_active': 'Active',
        }
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:  
            phone = re.sub(r'[^\d]', '', phone)
            
            if len(phone) < 10:
                raise ValidationError("Phone number must be at least 10 digits.")
            
            if User.objects.filter(phone=phone).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise ValidationError("This phone number is already in use.")
        
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email: 
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("Please enter a valid email address.")
            
            if len(email) > 50:
                raise ValidationError("Email cannot exceed 50 characters.")
            
            if User.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise ValidationError("This email address is already in use.")
        
        return email

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name: 
            if len(company_name) > 191:
                raise ValidationError("Company name cannot exceed 191 characters.")
            
            if User.objects.filter(company_name=company_name).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise ValidationError("This company name is already in use.")
        
        return company_name

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'Vendor' and not cleaned_data.get('company_name'):
            self.add_error('company_name', "Company name is required for Vendors.")
        
        return cleaned_data