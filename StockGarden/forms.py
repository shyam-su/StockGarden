from django import forms
from .models import *

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Brand'})
        }
        
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Category '})
        }
        
class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name','company_name','address','contact_no','email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Vendor Name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Company Name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address name'}),
            'contact_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact No.'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            
        }
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['vendor', 'name', 'description', 'price', 'Imei', 'image', 'categories', 'stock', 'brand', 'slug']
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Vendor Name'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Description', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price'}),
            'Imei': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter IMEI'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'categories': forms.Select(attrs={'class': 'form-control'}),  # Assuming many-to-many relation
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Stock Quantity'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),  # Assuming foreign key relation
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Slug'}),
        }

class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['name','product','quantity','price','total','contact_no','expiring_date']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'product': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Company Name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Quantity'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Total'}),
            'contact_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact No.'}),
            'expiring_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter Expiring Date'}),
            
        }
        def clean(self):
            cleaned_data = super().clean()
            quantity = cleaned_data.get('quantity')
            price = cleaned_data.get('price')

            # Calculate total automatically
            if quantity and price:
                cleaned_data['total'] = quantity * price

            return cleaned_data
        
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['vendor','product','description','quantity','price','total_value']
        widgets = {
            'vendor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Vendor'}),
            'product': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Description'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Quantity '}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price'}),
            'total_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Total Value'}),
            
        }
        
class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['name','product_name','device_model','issue_description','out_date','status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product Name'}),
            'device_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Device Model'}),
            'issue_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Issue Description '}),
            'out_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Out Date'}),
            'status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Status'}),
        }
        
class RepairDetailForm(forms.ModelForm):
    class Meta:
        model = RepairDetail
        fields = ['repair_order','repair_cost','fixed_description','repair_action']
        widgets = {
            'repair_order': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Repair Order'}),
            'repair_cost': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Repair Cost Name'}),
            'fixed_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Fixed Description'}),
            'repair_action': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Repair Action'}),
        }
        
        
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['name','product','price','quantity','total_price','payment_method','contact_no','status']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'product': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product Name'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price'}),
            'quantity': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Quantity'}),
            'total_price': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Total Price'}),
            'payment_method': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Payment Method'}),
            'contact_no': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Contact No'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter Status'}),
        }