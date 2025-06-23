from django.db import models
from user.models import User
from django.utils.text import slugify
import uuid
from decimal import Decimal
from PIL import Image
from django.db.models import Sum, Q, F, Case, When, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
import logging



logger = logging.getLogger(__name__)

# Create your models here.
class PaymentMethodChoices(models.TextChoices):
    CASH = 'cash', 'Cash'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    MOBILE_PAYMENT = 'mobile_payment', 'Mobile Payment'
    OTHER = 'other', 'Other'

class PaymentStatusChoices(models.TextChoices):
    FULL_PAYMENT = 'Full Payment', 'Full Payment'
    PARTIAL_PAYMENT = 'Partial Payment', 'Partial Payment'
    PENDING = 'Pending', 'Pending'
    OVERDUE = 'Overdue', 'Overdue'

class Company(models.Model):
    name = models.CharField(max_length=191,unique=True,verbose_name="Company Name")
    address = models.CharField(max_length=191)
    email = models.EmailField(max_length=191,db_index=True)
    phone_number = models.CharField(max_length=20,db_index=True)
    reg_no = models.CharField(max_length=20,unique=True,db_index=True)
    logo = models.ImageField(upload_to='company/logos/', blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
       
    
    class Meta:
        verbose_name = "Company"
        indexes = [models.Index(fields=['name'])]
        
class Brand(models.Model):
    name=models.CharField(max_length=191,unique=True,verbose_name="Brand Name",db_index=True)
    image = models.ImageField(upload_to='media/brands_imgs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Brand"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            img = img.resize((90, 25), Image.Resampling.LANCZOS)
            img.save(img_path)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=191,verbose_name="Category Name",unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Category"
        indexes = [models.Index(fields=['name'])]   

    def __str__(self):
        return self.name
    
class Purchase(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('needs_repair', 'Needs Repair'),
    ]
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="purchases") 
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL,null=True, related_name="purchases") 
    categories = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True, related_name="purchased_categories")
    product_name = models.CharField(max_length=191,verbose_name="Product Name",db_index=True)
    warranty = models.IntegerField(null=True, blank=True,)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    description = models.TextField(max_length=191, blank=True, null=True)
    Imei = models.CharField(max_length=100,unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='media/products_imgs/',null=True, blank=True)
    quantity = models.IntegerField()
    price = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) 
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH,db_index=True)
    payment_status=models.CharField(max_length=191,choices=PaymentStatusChoices, default='Pending',db_index=True,null=True,blank=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Purchase"
        indexes = [models.Index(fields=['product_name',])]
        
        
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price 
        self.remaining_amount = self.total_price - self.paid_amount
        if self.remaining_amount <= 0:
            self.payment_status = PaymentStatusChoices.FULL_PAYMENT
        elif self.paid_amount > 0:
            self.payment_status = PaymentStatusChoices.PARTIAL_PAYMENT
        else:
            self.payment_status = PaymentStatusChoices.PENDING
        super().save(*args, **kwargs)
       

    def __str__(self):
        return self.vendor.full_name
        
        
class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="products") 
    name = models.CharField(max_length=191, null=False, blank=False, verbose_name="Product Name")
    description = models.TextField(max_length=191,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=False, blank=False,verbose_name="Product Price",db_index=True)
    warranty = models.IntegerField(null=True, blank=True)
    Imei = models.CharField(max_length=100,null=True, blank=True)
    image = models.ImageField(upload_to='media/products_imgs/',null=True, blank=True)
    categories = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True, related_name="products") 
    stock=models.IntegerField(null=True, blank=True,db_index=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL,null=True, related_name="products") 
    slug = models.SlugField(max_length=191,null=True, blank=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product"
        indexes = [models.Index(fields=['name'])]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            unique_id = str(uuid.uuid4())[:8]
            self.slug = slugify(f"{self.name}-{unique_id}")
        super().save(*args, **kwargs)
        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            img = img.resize((90, 25), Image.Resampling.LANCZOS)
            img.save(img_path)


    def __str__(self):
        return self.name
    

class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)  
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=False, blank=False)
    Imei = models.CharField(max_length=100,unique=True, blank=True, null=True,db_index=True)
    warranty = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(blank=True, null=True)
    discount=models.IntegerField(null=True, blank=True, default=0)
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH,db_index=True)
    payment_status=models.CharField(max_length=191,choices=PaymentStatusChoices, default='Pending',db_index=True,null=True,blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.IntegerField()
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    due_date = models.DateTimeField(null=True, blank=True) 
    notes = models.TextField(null=True, blank=True) 
    created_at=models.DateTimeField(auto_now_add=True,verbose_name="Sale Date")
    updated_at=models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.price = self.price if self.price is not None else self.product.price
        self.warranty = self.product.warranty  
        self.total_amount = Decimal(self.quantity) * Decimal(self.price)
        self.paid_amount = Decimal(self.paid_amount)
        self.discount = Decimal(self.discount or 0) 
        self.remaining_amount = self.total_amount - self.paid_amount - self.discount
        if self.remaining_amount <= 0:
            self.payment_status = PaymentStatusChoices.FULL_PAYMENT
        elif self.paid_amount > 0:
            self.payment_status = PaymentStatusChoices.PARTIAL_PAYMENT
        else:
            self.payment_status = PaymentStatusChoices.PENDING
        super().save(*args, **kwargs)
            
    class Meta:
        verbose_name = "Sells"
        indexes = [models.Index(fields=['user',])]
    

    def __str__(self):
       return f"{self.user} - {self.product} - Quantity: {self.quantity} - Price: {self.price}"
 
class Repair(models.Model):
    STATUS_CHOICES = [
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('pending', 'Pending Pickup'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,related_name="user",blank=True,verbose_name="Customer Name")
    product_name = models.CharField(max_length=100) 
    device_model = models.CharField(max_length=100)
    issue_description = models.TextField() 
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH,db_index=True)
    payment_status=models.CharField(max_length=191,choices=PaymentStatusChoices, default='Pending',db_index=True,null=True,blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in-progress')
    out_date = models.DateTimeField(null=True, blank=True) 
    created_at=models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.paid_amount = Decimal(self.paid_amount)
        self.discount_amount = Decimal(self.discount_amount or 0) 
        self.remaining_amount = self.total_amount - self.paid_amount - self.discount_amount
        if self.remaining_amount <= 0:
            self.payment_status = PaymentStatusChoices.FULL_PAYMENT
        elif self.paid_amount > 0:
            self.payment_status = PaymentStatusChoices.PARTIAL_PAYMENT
        else:
            self.payment_status = PaymentStatusChoices.PENDING
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Repair"
        indexes = [models.Index(fields=['product_name',])]
    
    def __str__(self):
        return f"{self.device_model} - {self.status} ({self.user})"
    
class RepairDetail(models.Model):
    STATUS_CHOICES = [
        ('in', 'In'),
        ('repairing', 'Repairing'),
        ('repaired', 'Repaired'),
        ('returned', 'Returned'),
    ]
    repair_order = models.ForeignKey(Repair, on_delete=models.SET_NULL,null=True, related_name="details")  
    product_name=models.CharField(max_length=100)
    device_model=models.CharField(max_length=100)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    repair_detail_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    issue_description = models.TextField() 
    fixed_description = models.TextField() 
    repair_action = models.CharField(choices=STATUS_CHOICES, max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Repair Detail"
        indexes = [models.Index(fields=['product_name',])]
    
    def __str__(self):
        return f"{self.device_model}"

class Expense(models.Model):
    CATEGORY_TYPES = [
        ('selling', 'Selling Expenses'),
        ('admin', 'Administrative Expenses'),
        ('direct', 'Direct Costs'),
    ]
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices, default='cash',db_index=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='Pending',db_index=True,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Expense"


    def __str__(self):
        return f"{self.category_type} - {self.amount}"
 
class SalesInvoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    sales = models.ForeignKey(Sales, on_delete=models.SET_NULL,related_name="salesinvoice", null=True, blank=True)  
    product_name = models.CharField(max_length=255)
    quantity=models.IntegerField(null=True, blank=True)
    warranty = models.IntegerField(null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_number = models.BigIntegerField(null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.CASH,db_index=True)
    subtotal=models.IntegerField( null=True, blank=True)
    discount_amount = models.IntegerField( null=True, blank=True)
    total_amount = models.IntegerField( null=True, blank=True)
    paid_amount = models.IntegerField(default=0.00,null=True, blank=True)
    remaining_amount = models.IntegerField(default=0.00)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='Pending',db_index=True,null=True,blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # Ensure invoice number is correctly generated
            last_invoice = SalesInvoice.objects.order_by('-invoice_number').first()
            if last_invoice and last_invoice.invoice_number.startswith("SINV"):
                try:
                    last_invoice_number = int(last_invoice.invoice_number.replace("SINV", ""))
                    self.invoice_number = f"SINV{last_invoice_number + 1:06d}"
                except ValueError:
                    self.invoice_number = "SINV000001"
            else:
                self.invoice_number = "SINV000001"

        if self.sales and self.sales.product:
            product_price = round(self.sales.product.price)
            self.product_name = self.sales.product.name
            self.subtotal = (self.quantity or 0) * product_price

            self.discount_amount = min(self.discount_amount or 0, self.subtotal)  # Prevent discount > subtotal
            self.total_amount = self.subtotal - self.discount_amount
            self.remaining_amount = self.total_amount - (self.paid_amount or 0)

            # Ensure payment status is correct
            if self.remaining_amount <= 0:
                self.payment_status = 'Paid'
                self.remaining_amount = 0
            elif self.paid_amount > 0:
                self.payment_status = 'Partial'
            else:
                self.payment_status = 'Pending'

        # Ensure paid_amount does not exceed total_amount
        if self.paid_amount > self.total_amount:
            self.paid_amount = self.total_amount
            self.remaining_amount = 0

        super(SalesInvoice, self).save(*args, **kwargs)
    
    
    class Meta:
        verbose_name = "Sales Invoice"
        indexes = [models.Index(fields=['invoice_number',])]
    
    def __str__(self):
        return f"Sales Invoice {self.invoice_number} for Sale {self.customer_name}"


class RepairInvoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    repair = models.ForeignKey(Repair, on_delete=models.SET_NULL,related_name="repairinvoice", null=True, blank=True)  
    product_name = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    customer_number = models.BigIntegerField(null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.CASH,db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='Pending',db_index=True,null=True,blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            last_invoice = RepairInvoice.objects.all().order_by('-invoice_number').first()          
            if last_invoice and last_invoice.invoice_number.startswith("RINV"):
                last_invoice_number = int(last_invoice.invoice_number.replace("RINV", ""))
                self.invoice_number = f"RINV{last_invoice_number + 1:06d}" 
            else:
                self.invoice_number = "RINV0000001"  
        discount = self.discount_amount or 0
        subtotal = self.total_amount or 0
        
        # Ensure discount is not greater than the subtotal
        if discount > subtotal:
            discount = subtotal
            self.discount_amount = discount  # Update the discount to match the subtotal

        # Calculate total after discount
        total_after_discount = subtotal - discount
        
        # Update remaining amount based on paid_amount and total_after_discount
        self.remaining_amount = total_after_discount - (self.paid_amount or 0)

        if self.remaining_amount <= 0:
            self.payment_status = 'paid'
            self.remaining_amount = 0  
        elif self.paid_amount > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'Pending'
        super(RepairInvoice, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Repair Invoice"
        indexes = [models.Index(fields=['invoice_number',])]
    
    def __str__(self):
        return f"Repair Invoice {self.invoice_number} for Sale {self.customer_name}"

class Return(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.SET_NULL,null=True,related_name="invoice")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="product") 
    quantity_returned = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    return_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.product and self.product.price is not None:
            self.total_amount = self.product.price * self.quantity_returned
            self.refund_amount = self.total_amount  # Assuming full refund, adjust logic if needed
            

        
        super(Return, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Product Return"
        indexes = [models.Index(fields=['return_date'])]
    
    def __str__(self):
        return f"Return for Invoice #{self.invoice.invoice_number} - Product {self.product.name}"
    

class StockLedger(models.Model):
    """
    Tracks all inventory movements with running balances
    """
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('damage', 'Damage/Loss'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_ledger_entries')
    transaction_date = models.DateTimeField(auto_now_add=True, db_index=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_id = models.PositiveIntegerField()
    reference_model = models.CharField(max_length=50)
    quantity = models.IntegerField()  # Positive for incoming, negative for outgoing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    balance_quantity = models.IntegerField()
    balance_value = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Stock Ledger Entry"
        verbose_name_plural = "Stock Ledger Entries"
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.get_transaction_type_display()} - {self.quantity} units"
    
    def clean(self):
        if self.quantity == 0:
            raise ValidationError("Quantity cannot be zero")
        if self.unit_cost < 0:
            raise ValidationError("Unit cost cannot be negative")
    
    def save(self, *args, **kwargs):
        # Calculate total value
        self.total_value = Decimal(self.quantity) * Decimal(self.unit_cost)
        
        # Get previous balance for this product
        previous_entry = StockLedger.objects.filter(
            product=self.product
        ).exclude(id=self.id).order_by('-transaction_date', '-id').first()
        
        # Calculate running balances
        if previous_entry:
            self.balance_quantity = previous_entry.balance_quantity + self.quantity
            self.balance_value = previous_entry.balance_value + self.total_value
        else:
            self.balance_quantity = self.quantity
            self.balance_value = self.total_value
        
        # Validate balances won't go negative
        if self.balance_quantity < 0:
            raise ValidationError(f"This transaction would make stock negative for {self.product.name}")
        
        super().save(*args, **kwargs)
        
        # Update product stock
        self.product.stock = self.balance_quantity
        self.product.save(update_fields=['stock'])
        
        
class Report(models.Model):
    Total_sells = models.IntegerField(null=True, blank=True,db_index=True)
    Total_purchase = models.IntegerField(null=True, blank=True,db_index=True)
    Total_Stock=models.IntegerField(null=True, blank=True,db_index=True)
    Low_Stock=models.IntegerField(null=True, blank=True,db_index=True)
    Empty_Stock=models.IntegerField(null=True, blank=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.Total_Stock = Product.objects.aggregate(total=models.Sum('stock'))['total'] or 0
        self.Low_Stock = Product.objects.filter(stock__lte=5).count()
        self.Empty_Stock = Product.objects.filter(stock=0).count()
        super(Report, self).save(*args, **kwargs)

    
    class Meta:
        verbose_name = "Report"
        indexes = [models.Index(fields=['Total_sells',])]    


class Daybook(models.Model):
    """
    A chronological record of all financial transactions before posting to ledger
    """
    TRANSACTION_TYPES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('expense', 'Expense'),
        ('repair', 'Repair'),
        ('payment_received', 'Payment Received'),
        ('payment_made', 'Payment Made'),
        ('return', 'Return'),
    ]
    
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_id = models.CharField(max_length=50)  # Stores the ID of the related transaction
    reference_model = models.CharField(max_length=50)  # Stores the model name (e.g., 'Sales', 'Purchase')
    description = models.TextField()
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices.choices, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Daybook Entry"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['reference_id']),
        ]
    
    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.get_transaction_type_display()} - {self.description[:50]}"
    

class Cashbook(models.Model):
    """
    Records all cash and bank transactions (actual money movements)
    """
    ENTRY_TYPES = [
        ('receipt', 'Receipt'),
        ('payment', 'Payment'),
    ]
    
    SOURCE_TYPES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('expense', 'Expense'),
        ('repair', 'Repair'),
        ('return', 'Return'),
        ('other', 'Other'),
    ]
    
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES)
    reference_id = models.CharField(max_length=50)  # ID of the related transaction
    reference_model = models.CharField(max_length=50)  # Model name (e.g., 'Sales', 'Purchase')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices)
    is_bank = models.BooleanField(default=False)  # True for bank transactions, False for cash
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    cheque_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateField()  # Date when the transaction actually occurred
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Balance fields (calculated on save)
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bank_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-transaction_date', '-date']
        verbose_name = "Cashbook Entry"
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['entry_type']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['is_bank']),
        ]
    
    def __str__(self):
        return f"{self.transaction_date.strftime('%Y-%m-%d')} - {self.get_entry_type_display()} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Calculate balances
        if not self.pk:  # Only for new entries
            previous_entry = Cashbook.objects.filter(
                transaction_date__lte=self.transaction_date
            ).order_by('-transaction_date', '-id').first()
            
            if self.is_bank:
                prev_balance = previous_entry.bank_balance if previous_entry else Decimal('0.00')
                if self.entry_type == 'receipt':
                    self.bank_balance = prev_balance + self.amount
                    self.cash_balance = previous_entry.cash_balance if previous_entry else Decimal('0.00')
                else:
                    self.bank_balance = prev_balance - self.amount
                    self.cash_balance = previous_entry.cash_balance if previous_entry else Decimal('0.00')
            else:
                prev_balance = previous_entry.cash_balance if previous_entry else Decimal('0.00')
                if self.entry_type == 'receipt':
                    self.cash_balance = prev_balance + self.amount
                    self.bank_balance = previous_entry.bank_balance if previous_entry else Decimal('0.00')
                else:
                    self.cash_balance = prev_balance - self.amount
                    self.bank_balance = previous_entry.bank_balance if previous_entry else Decimal('0.00')
        
        super().save(*args, **kwargs)
        
class AccountType(models.TextChoices):
    ASSET = 'asset', 'Asset'
    LIABILITY = 'liability', 'Liability'
    EQUITY = 'equity', 'Equity'
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'

class Account(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = "Account"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['account_type']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        try:
            if self.parent_account and self.parent_account.parent_account == self:
                raise ValidationError("Circular reference in parent accounts is not allowed.")
        except Exception as e:
            logger.error(f"Error in Account.clean for {self.name}: {str(e)}")
            raise ValidationError(f"Failed to validate account: {str(e)}")

    def get_balance(self, start_date=None, end_date=None):
        try:
            qs = LedgerEntry.objects.filter(account=self)
            if start_date:
                qs = qs.filter(date__gte=start_date)
            if end_date:
                qs = qs.filter(date__lte=end_date)
            
            balance = qs.aggregate(
                total_debit=Coalesce(Sum('debit_amount'), Decimal('0.00')),
                total_credit=Coalesce(Sum('credit_amount'), Decimal('0.00'))
            )
            
            if self.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                return balance['total_debit'] - balance['total_credit']
            return balance['total_credit'] - balance['total_debit']
        except Exception as e:
            logger.error(f"Error calculating balance for account {self.code}: {str(e)}")
            return Decimal('0.00')

class LedgerEntry(models.Model):
    date = models.DateTimeField(db_index=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='ledger_entries')
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    reference = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    transaction_type = models.CharField(max_length=50)
    transaction_id = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = "Ledger Entry"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['account']),
            models.Index(fields=['transaction_type', 'transaction_id']),
        ]

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.account} - {self.description[:50]}"

    def clean(self):
        try:
            if self.debit_amount and self.credit_amount:
                raise ValidationError("A ledger entry cannot have both debit and credit amounts.")
            if not self.debit_amount and not self.credit_amount:
                raise ValidationError("A ledger entry must have either a debit or credit amount.")
            if self.debit_amount < 0 or self.credit_amount < 0:
                raise ValidationError("Amounts cannot be negative.")
        except Exception as e:
            logger.error(f"Error in LedgerEntry.clean for transaction {self.transaction_id}: {str(e)}")
            raise ValidationError(f"Failed to validate ledger entry: {str(e)}")

    def save(self, *args, **kwargs):
        try:
            previous_entries = LedgerEntry.objects.filter(
                account=self.account,
                date__lte=self.date
            ).exclude(id=self.id).order_by('-date', '-id')
            
            previous_balance = previous_entries.first().balance if previous_entries.exists() else Decimal('0.00')
            
            if self.debit_amount:
                self.balance = previous_balance + self.debit_amount
            else:
                self.balance = previous_balance - self.credit_amount
            
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving LedgerEntry for transaction {self.transaction_id}: {str(e)}")
            raise ValidationError(f"Failed to save ledger entry: {str(e)}")

class BalanceSheet(models.Model):
    report_date = models.DateField(unique=True)
    is_final = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    current_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    fixed_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    other_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    current_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    long_term_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    equity = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    retained_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-report_date']
        verbose_name = "Balance Sheet"
        verbose_name_plural = "Balance Sheets"

    def __str__(self):
        return f"Balance Sheet as of {self.report_date.strftime('%Y-%m-%d')}"

    def get_assets(self):
        try:
            asset_accounts = Account.objects.filter(account_type=AccountType.ASSET)
            balances = {
                'current': Decimal('0.00'),
                'fixed': Decimal('0.00'),
                'other': Decimal('0.00')
            }
            
            for account in asset_accounts:
                balance = account.get_balance(end_date=self.report_date)
                if account.code.startswith('1') or 'current' in account.name.lower():
                    balances['current'] += balance
                elif account.code.startswith('3') or 'fixed' in account.name.lower():
                    balances['fixed'] += balance
                else:
                    balances['other'] += balance
                
            self.current_assets = balances['current']
            self.fixed_assets = balances['fixed']
            self.other_assets = balances['other']
            return self.current_assets + self.fixed_assets + self.other_assets
        except Exception as e:
            logger.error(f"Error calculating assets for BalanceSheet {self.report_date}: {str(e)}")
            return Decimal('0.00')

    def get_liabilities(self):
        try:
            liability_accounts = Account.objects.filter(account_type=AccountType.LIABILITY)
            balances = {
                'current': Decimal('0.00'),
                'long_term': Decimal('0.00')
            }
            
            for account in liability_accounts:
                balance = account.get_balance(end_date=self.report_date)
                if account.code.startswith('2') or 'current' in account.name.lower():
                    balances['current'] += balance
                else:
                    balances['long_term'] += balance
                
            self.current_liabilities = balances['current']
            self.long_term_liabilities = balances['long_term']
            return self.current_liabilities + self.long_term_liabilities
        except Exception as e:
            logger.error(f"Error calculating liabilities for BalanceSheet {self.report_date}: {str(e)}")
            return Decimal('0.00')

    def get_equity(self):
        try:
            equity_accounts = Account.objects.filter(account_type=AccountType.EQUITY)
            self.equity = sum(account.get_balance(end_date=self.report_date) for account in equity_accounts)
            
            pl_statements = ProfitAndLoss.objects.filter(end_date__lte=self.report_date)
            self.retained_earnings = sum(pl.get_net_profit() for pl in pl_statements)
            
            return self.equity + self.retained_earnings
        except Exception as e:
            logger.error(f"Error calculating equity for BalanceSheet {self.report_date}: {str(e)}")
            return Decimal('0.00')

    def validate_balances(self):
        try:
            assets = self.get_assets()
            liabilities = self.get_liabilities()
            equity = self.get_equity()
            return abs(assets - (liabilities + equity)) < Decimal('0.01')
        except Exception as e:
            logger.error(f"Error validating balances for BalanceSheet {self.report_date}: {str(e)}")
            return False

    def save(self, *args, **kwargs):
        try:
            self.get_assets()
            self.get_liabilities()
            self.get_equity()
            if self.is_final and not self.validate_balances():
                raise ValidationError("Balance sheet does not balance. Assets must equal Liabilities plus Equity.")
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving BalanceSheet for {self.report_date}: {str(e)}")
            raise ValidationError(f"Failed to save balance sheet: {str(e)}")

class ProfitAndLoss(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    is_final = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    sales_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    other_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    cost_of_goods_sold = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    operating_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    other_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-end_date']
        verbose_name = "Profit and Loss"
        verbose_name_plural = "Profit and Loss Statements"
        constraints = [
                models.CheckConstraint(
                    check=Q(end_date__gte=F('start_date')),
                    name='end_date_after_start_date'
                )
            ]

    def __str__(self):
        return f"Profit and Loss for {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}"

    def get_revenue(self):
        try:
            revenue_accounts = Account.objects.filter(account_type=AccountType.INCOME)
            balances = {
                'sales': Decimal('0.00'),
                'other': Decimal('0.00')
            }
            
            for account in revenue_accounts:
                balance = account.get_balance(start_date=self.start_date, end_date=self.end_date)
                if 'sales' in account.name.lower() or account.code.startswith('4'):
                    balances['sales'] += balance
                else:
                    balances['other'] += balance
            self.sales_revenue = balances['sales']
            self.other_revenue = balances['other']
            return self.sales_revenue + self.other_revenue
        except Exception as e:
            logger.error(f"Error calculating revenue for ProfitAndLoss {self.start_date} to {self.end_date}: {str(e)}")
            return Decimal('0.00')

    def get_expenses(self):
        try:
            expense_accounts = Account.objects.filter(account_type=AccountType.EXPENSE)
            balances = {
                'cogs': Decimal('0.00'),
                'operating': Decimal('0.00'),
                'other': Decimal('0.00')
            }
            
            for account in expense_accounts:
                balance = account.get_balance(start_date=self.start_date, end_date=self.end_date)
                if 'cost of goods' in account.name.lower() or account.code.startswith('5'):
                    balances['cogs'] += balance
                elif 'operating' in account.name.lower() or account.code.startswith('6'):
                    balances['operating'] += balance
                else:
                    balances['other'] += balance
                    
            self.cost_of_goods = balances['cogs']
            self.operating_costs = balances['operating']
            self.other_expenses = balances['other']
            return self.cost_of_goods_sold + self.operating_expenses + self.other_expenses
        except Exception as e:
            logger.error(f"Error calculating expenses for ProfitAndLoss {self.start_date} to {self.end_date}: {str(e)}")
            return Decimal('0.00')

    def get_gross_profit(self):
        try:
            self.gross_profit = self.sales_revenue - self.cost_of_goods_sold
            return self.gross_profit
        except Exception as e:
            logger.error(f"Error calculating gross profit for ProfitAndLoss {self.start_date} to {self.end_date}: {str(e)}")
            return Decimal('0.00')

    def get_net_profit(self):
        try:
            self.net_profit = (self.sales_revenue + self.other_revenue) - \
                (self.cost_of_goods_sold + self.operating_expenses + self.other_expenses)
            return self.net_profit
        except Exception as e:
            logger.error(f"Error calculating net profit for ProfitAndLoss {self.start_date} to {self.end_date}: {str(e)}")
            return Decimal('0.00')

    def save(self, *args, **kwargs):
        try:
            if self.end_date.date < self.start_date:
                raise ValidationError("End date must be after start date.")
            self.get_revenue()
            self.get_expenses()
            self.get_gross_profit()
            self.get_net_profit()
            super().__init__(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving ProfitAndLoss for {self.start_date} to {self.end_date}: {str(e)}")
            raise ValidationError(f"Failed to save profit and loss statement: {str(e)}")
