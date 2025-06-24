from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.utils import timezone


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
            "warranty",
            "image",
            "quantity",
            "price",
            "paid_amount",
            "payment_method",
        ]
        widgets = {
            "vendor": forms.Select(attrs={"class": "form-control", "id": "vendor"}),
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
                    "rows": 1,
                }
            ),
            "warranty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Warranty",
                    "id": "warranty",
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
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
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
            "warranty": "warranty",
            "image": "Image",
            "price": "Price",
            "quantity": "Stock Quantity",
            "paid_amount": "Paid Amount",
            "payment_method": "Payment Method",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vendors = User.objects.filter(role="Vendor")
        self.fields["vendor"].queryset = vendors


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "vendor",
            "name",
            "description",
            "price",
            "warranty",
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
                    "rows": 1,
                    "id": "description",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Price",
                    "id": "price",
                    "readonly": "readonly",
                }
            ),
            "warranty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Warranty",
                    "id": "warranty",
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
                    "id": "image"
                }
            ),
            "categories": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "categories"
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Stock Quantity",
                    "id": "stock",
                }
            ),
            "brand": forms.Select(attrs={
                "class": "form-control",
                "id": "brand"
                }
        ),
        }
        labels = {
            "vendor": "Vendor Name",
            "brand": "Brand",
            "categories": "Categories",
            "name": "Product Name",
            "description": "Description",
            "price": "Price",
            "warranty": "warranty",
            "Imei": "Imei Number",
            "image": "Image",
            "stock": "Stock Quantity",
        }


class SalesForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False, 
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Customer Name",
                "id": "user",
            }
        ),
    )

    class Meta:
        model = Sales
        fields = [
            "user",
            "product",
            "Imei",
            "warranty",
            "quantity",
            "price",
            "discount",
            "payment_method",
            "paid_amount",
            "due_date",
            "notes",
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
            "Imei": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Imei",
                    "id": "Imei",
                }
            ),
            "warranty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Warranty",
                    "id": "warranty",
                    "min": "0",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Quantity",
                    "id": "quantity",
                    "min": "1",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Price",
                    "id": "price",
                }
            ),
            "discount": forms.NumberInput(
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
            "paid_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Paid Amount",
                    "id": "paid_amount",
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
        }
        labels = {
            "name": "Customer Name",
            "product": "Product Name",
            "Imei": "Imei",
            "warranty": "Warranty",
            "quantity": "Quantity",
            "price": "Price",
            "discount": "Discount",
            "payment_method": "Payment Method",
            "paid_amount": "Paid Amount",
            "due_date": "Due Date",
            "notes": "Notes",
        }


    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        instance = getattr(self, 'instance', None)  # Get the Sales instance being updated (if any)

        if product and quantity:
            available_stock = product.stock
            if instance and instance.pk:  # This is an update
                # Add back the original sales quantity to the available stock
                available_stock += instance.quantity

            if quantity > available_stock:
                raise ValidationError(f"Insufficient stock. Only {available_stock} items available.")

        return cleaned_data
    
    # Custom validation for quantity (should be at least 1)
    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity and quantity < 1:
            raise ValidationError("Quantity must be at least 1.")
        return quantity

    # Custom validation for price (must be positive)
    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price



    # Validate due date (must be in the future)
    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        if due_date and due_date < timezone.now():
            raise ValidationError("Due date cannot be in the past.")
        return due_date


class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = [
            "user",
            "product_name",
            "device_model",
            "issue_description",
            "payment_method",
            "total_amount",
            "paid_amount",
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
                    "rows": 1,
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
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
                    "type": "datetime-local",
                }
            ),
        }
        labels = {
            "name": "Customer Name",
            "product_name": "Product Name",
            "device_model": "Device Model",
            "issue_description": "Description",
            "payment_method": "Payment Method",
            "total_amount": "Total Amount",
            "paid_amount": "Paid Amount",
            "status": "Status",
            "out_date": "Out Date",
        }


class RepairDetailForm(forms.ModelForm):
    class Meta:
        model = RepairDetail
        fields = [
            "repair_order",
            "product_name",
            "device_model",
            "repair_cost",
            "repair_detail_cost",
            "issue_description",
            "fixed_description",
            "repair_action",
        ]
        widgets = {
            "repair_order": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Repair Order",
                    "id": "repair_order",
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
            "repair_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Repair Cost Name",
                    "id": "repair_cost",
                }
            ),
            "repair_detail_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Repair Detail Cost",
                    "id": "repair_detail_cost",
                }
            ),
            "issue_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Issue Description",
                    "rows": 1,
                    "id": "issue_description",
                }
            ),
            "fixed_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Fixed Description",
                    "id": "fixed_description",
                    "rows": 2,
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
            "product_name": "Product Name",
            "device_model": "Device Model",
            "repair_cost": "Repair Cost",
            "repair_detail_cost": "Repair Detail Cost",
            "issue_description": "Issue Description",
            "fixed_description": "Issue Fixed Description",
            "repair_action": "Repair Action",
        }

    def __init__(self, *args, **kwargs):
        super(RepairDetailForm, self).__init__(*args, **kwargs)
        self.fields["repair_order"].queryset = Repair.objects.exclude(
            status="completed"
        )


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category_type", "amount", "description", "payment_method"]
        widgets = {
            "category_type": forms.Select(
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
                    "rows": 1,
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
                }
            ),
        }
        labels = {
            "category": "Category",
            "amount": "Amount",
            "description": "Description",
            "payment_method": "Payment Method",
        }


class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        fields = [
            "sales",
            "product_name",
            "warranty",
            "customer_name",
            "customer_number",
            "customer_address",
            "payment_method",
            "discount_amount",
            "paid_amount",
            "due_date",
            "notes",
        ]
        widgets = {
            "sales": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Sales",
                    "id": "sales",
                }
            ),
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Product Name",
                    "id": "product_name",
                }
            ),
            "warranty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Warranty",
                    "id": "warranty",
                }
            ),
            "customer_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Customer Name",
                    "id": "customer_name",
                }
            ),
            "customer_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Customer Number",
                    "id": "customer_number",
                }
            ),
            "customer_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Customer Address",
                    "id": "customer_address",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
                }
            ),
            "discount_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Discount Amount",
                    "id": "discount_amount",
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
                    "rows": 1,
                }
            ),
        }
        labels = {
            "sales": "Sales",
            "product_name": "Product Name",
            "warranty": "Warranty (in months)",
            "customer_name": "Customer Name",
            "customer_number": "Customer Number",
            "customer_address": "Customer Address",
            "payment_method": "Payment Method",
            "discount_amount": "Discount Amount",
            "paid_amount": "Paid Amount",
            "due_date": "Due Date",
            "notes": "Notes",
        }


class RepairInvoiceForm(forms.ModelForm):
    class Meta:
        model = RepairInvoice
        fields = [
            "repair",
            "product_name",
            "customer_name",
            "customer_number",
            "customer_address",
            "payment_method",
            "discount_amount",
            "paid_amount",
            "due_date",
            "notes",
        ]
        widgets = {
            "repair": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Repair",
                    "id": "repair",
                }
            ),
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Product Name",
                    "id": "product_name",
                }
            ),
            "customer_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Customer Name",
                    "id": "customer_name",
                }
            ),
            "customer_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Customer Number",
                    "id": "customer_number",
                }
            ),
            "customer_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Customer Address",
                    "id": "customer_address",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Select Payment Method",
                    "id": "payment_method",
                }
            ),
            "discount_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Discount Amount",
                    "id": "discount_amount",
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
                    "placeholder": "Add notes (e.g., 'Half paid, rest next week')",
                    "id": "notes",
                    "rows": 1,
                }
            ),
        }
        labels = {
            "invoice_number": "Invoice Number",
            "repair": "Repair",
            "product_name": "Product Name",
            "customer_name": "Customer Name",
            "customer_number": "Customer Number",
            "customer_address": "Customer Address",
            "payment_method": "Payment Method",
            "discount_amount": "Discount Amount",
            "paid_amount": "Paid Amount",
            "due_date": "Due Date",
            "notes": "Notes",
        }


class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = [
            "invoice",
            "product",
            "quantity_returned",
            "reason",
            "total_amount",
            "refund_amount",
        ]
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
                    "rows": 2,
                }
            ),
            "total_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Total Amount",
                    "id": "total_amount",
                }
            ),
            "refund_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Refund Amount",
                    "id": "refund_amount",
                }
            ),
        }
        labels = {
            "invoice": "Invoice",
            "product": "Product",
            "quantity_returned": "Quantity Returned",
            "reason": "Reason",
            "total_amount": "Total Amount",
            "refund_amount": "Refund Amount",
        }
        
class StockLedgerForm(forms.ModelForm):
    class Meta:
        model = StockLedger
        fields = [
            'product', 
            'transaction_type', 
            'reference_id', 
            'reference_model', 
            'quantity', 
            'unit_cost', 
            'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        
        if quantity == 0:
            raise forms.ValidationError("Quantity cannot be zero")
        
        return cleaned_data
    
class DaybookForm(forms.ModelForm):
    class Meta:
        model = Daybook
        fields = [
            # Remove 'date' from the fields list since it's auto_now_add
            'transaction_type',
            'reference_id',
            'reference_model',
            'description',
            'debit_amount',
            'credit_amount',
            'payment_method',
            'payment_status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        
        if debit_amount == 0 and credit_amount == 0:
            raise forms.ValidationError("Both debit and credit amounts cannot be zero")
        
        return cleaned_data
    
    
class CashbookForm(forms.ModelForm):
    transaction_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    class Meta:
        model = Cashbook
        fields = [
            'entry_type',
            'source_type',
            'reference_id',
            'reference_model',
            'description',
            'amount',
            'payment_method',
            'is_bank',
            'bank_name',
            'cheque_number',
            'transaction_date',
            'notes',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Make bank fields required conditionally
        self.fields['bank_name'].required = False
        self.fields['cheque_number'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        is_bank = cleaned_data.get('is_bank')
        bank_name = cleaned_data.get('bank_name')
        cheque_number = cleaned_data.get('cheque_number')
        amount = cleaned_data.get('amount')
        
        if is_bank:
            if not bank_name:
                self.add_error('bank_name', "Bank name is required for bank transactions")
            
            payment_method = cleaned_data.get('payment_method')
            if payment_method == 'cheque' and not cheque_number:
                self.add_error('cheque_number', "Cheque number is required for cheque payments")
        
        if amount is not None and amount <= 0:
            self.add_error('amount', "Amount must be greater than zero")
        
        return cleaned_data
    

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name', 'account_type', 'parent_account', 'is_active', 'description']
        
    def clean(self):
        cleaned_data = super().clean()
        parent_account = cleaned_data.get('parent_account')
        
        # Prevent circular references
        if parent_account and parent_account.parent_account == self.instance:
            raise ValidationError("Circular reference in parent accounts is not allowed.")
        return cleaned_data

class LedgerEntryForm(forms.ModelForm):
    class Meta:
        model = LedgerEntry
        fields = ['date', 'account', 'debit_amount', 'credit_amount', 
                 'reference', 'description', 'transaction_type', 'transaction_id']
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount', 0)
        credit_amount = cleaned_data.get('credit_amount', 0)
        
        if debit_amount and credit_amount:
            raise ValidationError("A ledger entry cannot have both debit and credit amounts.")
        if not debit_amount and not credit_amount:
            raise ValidationError("A ledger entry must have either a debit or credit amount.")
        if debit_amount < 0 or credit_amount < 0:
            raise ValidationError("Amounts cannot be negative.")
        
        return cleaned_data

class BalanceSheetForm(forms.ModelForm):
    class Meta:
        model = BalanceSheet
        fields = ['report_date', 'is_final', 'notes']

class ProfitAndLossForm(forms.ModelForm):
    class Meta:
        model = ProfitAndLoss
        fields = ['start_date', 'end_date', 'is_final', 'notes']
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name', 'account_type', 'parent_account', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[A-Za-z0-9]+',
                'title': 'Code must be alphanumeric',
                'required': 'required',
                'placeholder': 'Enter account code (e.g., 1001)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'placeholder': 'Enter account name'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'parent_account': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter description (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isalnum():
            raise forms.ValidationError("Code must be alphanumeric.")
        return code

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        # Exclude the current account from parent_account choices to prevent self-referencing
        if instance:
            self.fields['parent_account'].queryset = Account.objects.exclude(pk=instance.pk)
        else:
            self.fields['parent_account'].queryset = Account.objects.all()