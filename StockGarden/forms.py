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


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            "vendor",
            "brand",
            "categories",
            "product_name",
            "condition",
            "description",
            "Imei",  
            "image",
            "quantity",
            "price",
            "paid_amount",
            "remaining_amount",
        ]
        widgets = {
             "vendor": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "vendor"
                    }
            ),
            "brand": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "brand",
                }
            ),
            "categories": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "categories",
                }
            ),
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Product Name",
                    "id": "product_name",
                }
            ),
            "condition": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "condition",
                }
            ),
            "description": forms.Textarea( 
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Description",
                    "id": "description",
                    "rows": 3,
                }
            ),
            "Imei": forms.TextInput( 
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter IMEI",
                    "id": "Imei",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "id": "image",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Price",
                    "id": "price",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Quantity",
                    "id": "quantity",
                }
            ),
            "paid_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Paid Amount",
                    "id": "paid_amount",
                    "step": "0.01",
                }
            ),
            "remaining_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Remaining Amount",
                    "id": "remaining_amount",
                }
            ),
        }
        labels = {
            "vendor": "Vendor Name",
            "brand": "Brand",
            "categories": "Categories",
            "product_name": "Product Name",
            "condition": "Condition",
            "description": "Description",
            "Imei": "IMEI Number",  
            "image": "Image",
            "price": "Price",
            "quantity": "Stock Quantity",
            "remaining_amount": "Remaining Amount",
            "paid_amount": "Paid Amount",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vendors = User.objects.filter(role='Vendor')
        self.fields['vendor'].queryset = vendors
        
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
            "user",
            "product",
            "Imei",
            "quantity",
            "price",
            'discount',
            'payment_method',
            'payment_status',
            'total_amount',
            'paid_amount',
            'remaining_amount',
            'due_date',
            'notes',
            "expiring_date",
        ]
        widgets = {
            "user": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Name",
                    "id": "user",
                }
            ),
            "product": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Company Name",
                    "id": "product",
                }
            ),
            "Imei": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Imei",
                    "id": "Imei",
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
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
                }
            ),
            "payment_status": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Status",
                    "id": "stpayment_statusatus",
                }
            ),
            "total_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Total Amount",
                    "id": "total_amount",
                    "step": "0.01",
                }
            ),
            "paid_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Paid Amount",
                    "id": "paid_amount",
                    "step": "0.01",
                }
            ),
            "remaining_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Remaining Amount",
                    "id": "remaining_amount",
                    "step": "0.01",
                }
            ),
            "due_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Due Date",
                    "id": "due_date",
                    "type": "datetime-local",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Add payment notes (e.g., 'Will pay 500 later')",
                    "id": "notes",
                    "rows": 3,
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
            "Imei": "Imei",
            "quantity": "Quantity",
            "price": "Price",
            "discount": "Discount",
            "payment_method": "Payment Method",
            "payment_status": "Payment Status",
            "total_amount": "Total Amount",
            "paid_amount": "Paid Amount",
            "remaining_amount": "Remaining Amount",
            "due_date": "Due Date",
            "notes": "Notes",
            "expiring_date": "Expiring Date",
        }

class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = [
            "user",
            "product_name",
            "device_model",
            "issue_description",
            "payment_method",
            "payment_status",
            "total_amount",
            "paid_amount",
            "remaining_amount",
            "status",
            "out_date",
        ]
        widgets = {
            "user": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Name",
                    "id": "user",
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
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
                }
            ),
            "payment_status": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Status",
                    "id": "stpayment_statusatus",
                }
            ),
            "total_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Total Amount",
                    "id": "total_amount",
                    "step": "0.01",
                }
            ),
            "paid_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Paid Amount",
                    "id": "paid_amount",
                    "step": "0.01",
                }
            ),
            "remaining_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Remaining Amount",
                    "id": "remaining_amount",
                    "step": "0.01",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Status",
                    "id": "status",
                }
            ),
            "out_date": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Out Date",
                    "id": "out_date",
                }
            ),
        }
        labels = {
            "name": "Customer Name",
            "product_name": "Product Name",
            "device_model": "Device Model",
            "issue_description": "Description",
            "payment_method": "Payment Method",
            "payment_status": "Payment Status",
            "total_amount": "Total Amount",
            "paid_amount": "Paid Amount",
            "remaining_amount": "Remaining Amount",
            "status": "Status",
            "out_date": "Out Date",
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

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'payment_method', 'payment_status']
        widgets = {
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Category",
                    "id": "category",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "id": "amount",
                    "step": "0.01",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Description",
                    "id": "description",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
                }
            ),
            "payment_status": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Status",
                    "id": "payment_status",
                }
            ),
        }
        labels = {
            "category": "Category",
            "amount": "Amount",
            "description": "Description",
            "payment_method": "Payment Method",
            "payment_status": "Payment Status",
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'payment_method', 'payment_status']
        widgets = {
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Category",
                    "id": "category",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "id": "amount",
                    "step": "0.01",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Description",
                    "id": "description",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
                }
            ),
            "payment_status": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Status",
                    "id": "payment_status",
                }
            ),
        }
        labels = {
            "category": "Category",
            "amount": "Amount",
            "description": "Description",
            "payment_method": "Payment Method",
            "payment_status": "Payment Status",
        }
class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        fields = ['sales', 'customer_name', 'payment_method','discount_amount', 'total_amount', 'payment_status', 'due_date',]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "id": "amount",
                    "step": "0.01",
                }
            ),
            "payment_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Date",
                    "id": "payment_date",
                    "type": "datetime-local",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Add notes (e.g., 'Half paid, rest next week')",
                    "id": "notes",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "amount": "Amount",
            "payment_method": "Payment Method",
            "payment_date": "Payment Date",
            "notes": "Notes",
        }
        
class RepairInvoiceForm(forms.ModelForm):
    class Meta:
        model = RepairInvoice
        fields = ['repair', 'customer_name', 'payment_method','discount_amount', 'total_amount', 'payment_status', 'due_date',]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Amount",
                    "id": "amount",
                    "step": "0.01",
                }
            ),
            "payment_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Date",
                    "id": "payment_date",
                    "type": "datetime-local",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Add notes (e.g., 'Half paid, rest next week')",
                    "id": "notes",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "amount": "Amount",
            "payment_method": "Payment Method",
            "payment_date": "Payment Date",
            "notes": "Notes",
        }

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['invoice', 'product', 'quantity_returned', 'reason','refund_amount']
        widgets = {
            "invoice": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Invoice",
                    "id": "invoice",
                }
            ),
            "product": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Product",
                    "id": "product",
                }
            ),
            "quantity_returned": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Quantity Returned",
                    "id": "quantity_returned",
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Reason",
                    "id": "reason",
                }
            ),
            "refund_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Refund Amount",
                    "id": "refund_amount",
                    "step": "0.01",
                }
            ),
        }
        labels = {
            "invoice": "Invoice",
            "product": "Product",
            "quantity_returned": "Quantity Returned",
            "reason": "Reason",
            "refund_amount": "Refund Amount",
        }