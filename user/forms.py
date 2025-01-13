from django import forms
from .models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name','address','phone','email','role','is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Full Name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Role'}),
            'is_active': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Active'}),
        }