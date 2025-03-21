from django import forms
from .models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name','address','phone','email','role','is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Full Name','id':'full_name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address','id':'address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone','id':'phone'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email','id':'email'}),
            'role': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Role','id':'role'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'is_active'}),  # Use CheckboxInput for BooleanField
        }
        labels = {
            'full_name': 'Full Name',
            'address': 'Address',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'role': 'Role',
            'is_active': 'Active',
        }