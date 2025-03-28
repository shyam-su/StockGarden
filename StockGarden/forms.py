from django import forms
from .models import *


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name", "image"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Brand",
                    "id": "brand_name",
                }
            ),
            "image": forms.FileInput(attrs={"class": "form-control", "id": "image"}),
        }
        labels = {
            "name": "Brand Name",
            "image": "Image ",
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Category ",
                    "id": "category_name",
                }
            ),
        }
        labels = {
            "name": "Category Name",
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["name", "company_name", "address", "contact_no", "email"]
        widgets = {
            "name": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Vendor Name",
                    "id": "vendor_name",
                }
            ),
            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Company Name",
                    "id": "company_name",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Address",
                    "rows": 3,
                    "id": "address",
                }
            ),
            "contact_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Contact Number",
                    "id": "contact_no",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Email Address",
                    "id": "email",
                }
            ),
        }
        labels = {
            "name": "Vendor Name",
            "company_name": "Company Name",
            "address": "Address",
            "contact_no": "Contact Number",
            "email": "Email Address",
        }
        
    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
        self.fields["name"].queryset = User.objects.filter(role="Vendor")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "vendor",
            "name",
            "description",
            "price",
            "Imei",
            "image",
            "categories",
            "stock",
            "brand",
        ]
        widgets = {
            "vendor": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Vendor Name",
                    "id": "vendor",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Product Name",
                    "id": "name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Description",
                    "rows": 3,
                    "id": "description",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Price",
                    "id": "price",
                    "readonly": "readonly"

                }
            ),
            "Imei": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter IMEI",
                    "id": "Imei",
                }
            ),
            "image": forms.FileInput(attrs={"class": "form-control", "id": "image"}),
            "categories": forms.Select(
                attrs={"class": "form-control", "id": "categories"}
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Stock Quantity",
                    "id": "stock",
                }
            ),
            "brand": forms.Select(attrs={"class": "form-control", "id": "brand"}),
        }
        labels = {
            "vendor": "Vendor Name",
            "name": "Product Name",
            "description": "Description",
            "price": "Price",
            "Imei": "Imei Number",
            "image": "Image",
            "categories": "Categories",
            "stock": "Stock Quantity",
            "brand": "Brand",
        }


class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = [
            "name",
            "product",
            "quantity",
            "price",
            "contact_no",
            "expiring_date",
        ]
        widgets = {
            "name": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Name",
                    "id": "name",
                }
            ),
            "product": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Company Name",
                    "id": "product",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Quantity",
                    "id": "quantity",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Price",
                    "id": "price",
                    "readonly": "readonly"
                    
                }
            ),
            "contact_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Contact No.",
                    "id": "contact_no",
                }
            ),
            "expiring_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Expiring Date",
                    "id": "expiring_date",
                }
            ),
        }
        labels = {
            "name": "Customer Name",
            "product": "Product Name",
            "quantity": "Quantity",
            "price": "Price",
            "contact_no": "Contact No",
            "expiring_date": "Expiring Date",
        }



class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            "vendor",
            "product",
            "description",
            "quantity",
            "price",
        ]
        widgets = {
            "vendor": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Vendor",
                    "id": "vendor",
                }
            ),
            "product": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Product",
                    "id": "product",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Description",
                    "id": "description",
                }
            ),
            "quantity": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Quantity ",
                    "id": "quantity",
                }
            ),
            "price": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Price",
                    "id": "price",
                }
            ),
        }
        labels = {
            "vendor": "Vendor Name",
            "product": "Product Name",
            "description": "Description",
            "quantity": "Quantity",
            "price": "Price",
        }


class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = [
            "name",
            "product_name",
            "device_model",
            "issue_description",
            "out_date",
            "status",
        ]
        widgets = {
            "name": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Name",
                    "id": "name",
                }
            ),
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Product Name",
                    "id": "product_name",
                }
            ),
            "device_model": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Device Model",
                    "id": "device_model",
                }
            ),
            "issue_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Issue Description ",
                    "id": "issue_description",
                }
            ),
            "out_date": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Out Date",
                    "id": "out_date",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Status",
                    "id": "status",
                }
            ),
        }
        labels = {
            "name": "Customer Name",
            "product_name": "Product Name",
            "device_model": "Device Model",
            "issue_description": "Description",
            "out_date": "Out Date",
            "status": "Status",
        }


class RepairDetailForm(forms.ModelForm):
    class Meta:
        model = RepairDetail
        fields = ["repair_order", "repair_cost", "fixed_description", "repair_action"]
        widgets = {
            "repair_order": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Repair Order",
                    "id": "repair_order",
                }
            ),
            "repair_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Repair Cost Name",
                    "id": "repair_cost",
                }
            ),
            "fixed_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Fixed Description",
                    "id": "fixed_description",
                }
            ),
            "repair_action": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Repair Action",
                    "id": "repair_action",
                }
            ),
        }
        labels = {
            "repair_order": "Repair Order",
            "repair_cost": "Repair Cost",
            "fixed_description": "Issue Fixed Description",
            "repair_action": "Repair Action",
        }

    def __init__(self, *args, **kwargs):
        super(RepairDetailForm, self).__init__(*args, **kwargs)
        # Filter out repair orders that are marked as completed
        self.fields["repair_order"].queryset = Repair.objects.exclude(status="completed")

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'sales',
            'discount',
            "payment_method",
            "status",
        ]
        widgets = {
            "sales": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Sales",
                    "id": "sales",
                }
            ),
            "discount": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Discount",
                    "id": "discount",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Payment Method",
                    "id": "payment_method",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Status",
                    "id": "status",
                }
            ),
        }
        labels = {
            "sales": "Customer Name",
            "discount": "Customer Name",
            "payment_method": "Payment Method",
            "status": "Status",
        }
