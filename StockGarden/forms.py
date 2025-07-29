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


class PurchaseVoucherForm(forms.ModelForm):
    class Meta:
        model = PurchaseVoucher
        fields = [
            "date", 
            "vendor",
            "discount",
            "payment_method",
            "status"
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "id": "purchase-date"
                }
            ),
            "vendor": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "vendor-select"
                }
            ),
            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "id": "discount-input",
                    "step": "0.01"
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "payment-method"
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "status-select"
                }
            )
        }
        labels = {
            "date": "Purchase Date",
            "vendor": "Vendor",
            "discount": "Discount Amount",
            "payment_method": "Payment Method",
            "status": "Voucher Status"
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter vendors only
        self.fields["vendor"].queryset = User.objects.filter(role="Vendor")
        
        # Set default date to today
        self.fields["date"].initial = timezone.now().date()
        
        # Add payment status choices dynamically
        self.fields["payment_method"].choices = PaymentMethodChoices.choices

class PurchaseItemForm(forms.ModelForm):
    # Add a field for new brand creation
    new_brand = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new brand name",
            "id": "new-brand"
        }),
        label="Or Create New Brand"
    )
    
    # Add a field for new category creation
    new_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new category name",
            "id": "new-category"
        }),
        label="Or Create New Category"
    )

    class Meta:
        model = PurchaseItem
        fields = [
            "brand",
            "category",
            "product_name",
            "condition",
            "description",
            "imei",
            "warranty",
            "image",
            "quantity",
            "price",
            "paid_amount",
        ]
        widgets = {
            "brand": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "brand-select"
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "category-select"
                }
            ),
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Product Name",
                    "id": "product-name"
                }
            ),
            "condition": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "condition-select"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Description",
                    "id": "description",
                    "rows": 2
                }
            ),
            "imei": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter IMEI Number",
                    "id": "imei-input"
                }
            ),
            "warranty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Warranty in months",
                    "id": "warranty-input"
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "id": "item-image"
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Quantity",
                    "id": "quantity-input",
                    "min": 1
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Unit Price",
                    "id": "price-input",
                    "step": "0.01"
                }
            ),
            "paid_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Amount Paid",
                    "id": "paid-amount",
                    "step": "0.01"
                }
            ),
    
        }
        labels = {
            "imei": "IMEI/Serial Number",
            "warranty": "Warranty (months)",
            "paid_amount": "Amount Paid for Item"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add condition choices
        self.fields["condition"].choices = PurchaseItem.CONDITION_CHOICES

    def clean(self):
        cleaned_data = super().clean()
        
        # Handle new brand creation
        new_brand = cleaned_data.get("new_brand")
        brand = cleaned_data.get("brand")
        
        if new_brand and not brand:
            # Create new brand
            brand, created = Brand.objects.get_or_create(name=new_brand.strip())
            cleaned_data["brand"] = brand
        
        # Handle new category creation
        new_category = cleaned_data.get("new_category")
        category = cleaned_data.get("category")
        
        if new_category and not category:
            # Create new category
            category, created = Category.objects.get_or_create(name=new_category.strip())
            cleaned_data["category"] = category
        
        # Validate IMEI
        imei = cleaned_data.get("imei")
        if imei == "":
            cleaned_data["imei"] = None
            
        # Validate paid amount doesn't exceed total
        quantity = cleaned_data.get("quantity", 0)
        price = cleaned_data.get("price", 0)
        paid_amount = cleaned_data.get("paid_amount", 0)
        
        total_price = quantity * price
        if paid_amount > total_price:
            raise ValidationError("Paid amount cannot exceed total price for this item")
        
        return cleaned_data


class ProductForm(forms.ModelForm):
    # Add fields for new brand/category creation
    new_brand = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new brand name",
            "id": "new-brand"
        }),
        label="Or Create New Brand"
    )
    
    new_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new category name",
            "id": "new-category"
        }),
        label="Or Create New Category"
    )

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
            "categories",  # Changed from 'categories' to match model
            "stock",
            "brand",
        ]
        widgets = {
            "vendor": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "product-vendor"
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Product Name",
                    "id": "product-name"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Product Description",
                    "rows": 2,
                    "id": "product-description"
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Selling Price",
                    "id": "product-price",
                    "step": "0.01"
                }
            ),
            "warranty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Warranty in months",
                    "id": "product-warranty"
                }
            ),
            "Imei": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "IMEI/Serial Number",
                    "id": "product-imei"
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "id": "product-image"
                }
            ),
            "categories": forms.Select(  # Changed to match model field name
                attrs={
                    "class": "form-control",
                    "id": "product-category"
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Stock Quantity",
                    "id": "product-stock",
                    "min": 0
                }
            ),
            "brand": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "product-brand"
                }
            ),
        }
        labels = {
            "imei": "IMEI/Serial Number",
            "categories": "Category",  # Updated label
            "stock": "Stock Quantity"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter vendors only
        self.fields["vendor"].queryset = User.objects.filter(role="Vendor")
        
        # Make price editable for new products
        if not self.instance.pk:
            self.fields["price"].widget.attrs.pop("readonly", None)

    def clean(self):
        cleaned_data = super().clean()
        
        # Handle new brand creation
        new_brand = cleaned_data.get("new_brand")
        brand = cleaned_data.get("brand")
        
        if new_brand and not brand:
            brand, created = Brand.objects.get_or_create(name=new_brand.strip())
            cleaned_data["brand"] = brand
        
        # Handle new category creation
        new_category = cleaned_data.get("new_category")
        category = cleaned_data.get("categories")
        
        if new_category and not category:
            category, created = Category.objects.get_or_create(name=new_category.strip())
            cleaned_data["categories"] = category
        
        # Validate IMEI
        imei = cleaned_data.get("Imei")
        if imei == "":
            cleaned_data["Imei"] = None
            
        return cleaned_data


class SalesVoucherForm(forms.ModelForm):
    # Field for new customer creation
    new_customer = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter customer name",
            "id": "new-customer"
        }),
        label="Or Create New Customer"
    )

    class Meta:
        model = SalesVoucher
        fields = [
            "date",
            "customer",
            "discount",
            "payment_method",
            "paid_amount",
            "status"
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "id": "sales-date"
                }
            ),
            "customer": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "customer-select"
                }
            ),
            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "id": "sales-discount",
                    "step": "0.01"
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "sales-payment-method"
                }
            ),
            "paid_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Amount Paid",
                    "id": "sales-paid-amount",
                    "step": "0.01"
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "sales-status"
                }
            )
        }
        labels = {
            "customer": "Customer",
            "paid_amount": "Amount Paid"
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Handle new customer creation
        new_customer = cleaned_data.get("new_customer")
        customer = cleaned_data.get("customer")
        
        if new_customer and not customer:
            # Create new customer
            customer = Customer.objects.create(name=new_customer.strip())
            cleaned_data["customer"] = customer
            
        return cleaned_data

class SalesItemForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = [
            "product",
            "quantity",
            "price",
            "warranty",
            "condition",
            "imei"
        ]
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "sales-product"
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "id": "sales-quantity"
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "id": "sales-price"
                }
            ),
            "warranty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "id": "sales-warranty"
                }
            ),
            "condition": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "sales-condition"
                }
            ),
            "imei": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "IMEI/Serial Number",
                    "id": "sales-imei"
                }
            )
        }
        labels = {
            "imei": "IMEI/Serial Number"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add condition choices
        self.fields["condition"].choices = SalesItem.CONDITION_CHOICES

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity", 0)
        imei = cleaned_data.get("imei")
        
        # Convert empty IMEI to None
        if imei == "":
            cleaned_data["imei"] = None
        
        # Stock validation
        if product and quantity:
            if quantity > product.stock:
                raise ValidationError(
                    f"Insufficient stock. Only {product.stock} available."
                )
        
        return cleaned_data


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
            "sales_voucher",
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
            "sales_voucher": forms.Select(
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
            "sales_voucher": "Sales Voucher",
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
    

