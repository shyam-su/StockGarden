from django.db import models,transaction
from user.models import User
from django.utils.text import slugify
import uuid
from decimal import Decimal
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
import logging
from django.core.validators import MinValueValidator
from django.utils import timezone
import decimal

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
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Brand"
        indexes = [models.Index(fields=['name'])]
    
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

class PurchaseVoucher(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    voucher_number = models.CharField(max_length=50, unique=True, editable=False)
    date = models.DateField(default=timezone.now)  # Added missing date field
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH)
    payment_status = models.CharField(max_length=20,choices=PaymentStatusChoices.choices,default=PaymentStatusChoices.PENDING)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)
    vendor = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="purchase_vouchers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Purchase Voucher"
        ordering = ['-date']  # Now references the actual date field
        indexes = [
            models.Index(fields=['voucher_number']),
            models.Index(fields=['date']),
        ]

    def save(self, *args, **kwargs):
        # Generate voucher number only once
        if not self.voucher_number:
            with transaction.atomic():
                last_voucher = PurchaseVoucher.objects.select_for_update().filter(
                    voucher_number__startswith="PV"
                ).order_by('-voucher_number').first()
                
                if last_voucher:
                    try:
                        last_num = int(last_voucher.voucher_number[2:])
                        self.voucher_number = f"PV{last_num + 1:06d}"
                    except (ValueError, IndexError):
                        self.voucher_number = "PV000001"
                else:
                    self.voucher_number = "PV000001"
        
        # Single save operation
        super().save(*args, **kwargs)

    def update_totals(self):
        """Calculate and update voucher totals - called by signal"""
        items = self.items.all()
        if items.exists():
            total = sum(item.total_price for item in items)
            cost = total - self.discount
            
            # Update without triggering save again
            PurchaseVoucher.objects.filter(pk=self.pk).update(
                total_amount=total,
                cost=cost
            )

    def __str__(self):
        return f"Purchase Voucher {self.voucher_number}"


class PurchaseItem(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('needs_repair', 'Needs Repair'),
    ]
    ITEM_TYPE_CHOICES = [
        ('sales', 'Sales'),
        ('repair', 'Repair'),
        ('other', 'Other'),
    ]
    voucher = models.ForeignKey(PurchaseVoucher,on_delete=models.CASCADE,related_name="items")
    brand = models.ForeignKey('Brand',on_delete=models.SET_NULL,null=True,related_name="purchased_items") 
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="purchased_items")
    product_name = models.CharField(max_length=191,verbose_name="Product Name",db_index=True)
    item_type= models.CharField(max_length=50,choices=ITEM_TYPE_CHOICES,default='sales')
    warranty = models.IntegerField(null=True,blank=True,validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=20,choices=CONDITION_CHOICES,default='new')
    description = models.CharField(max_length=191,blank=True,null=True)
    model_number = models.CharField(max_length=100,unique=True,blank=True,null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=12,decimal_places=2,default=0.00,editable=False) 
    paid_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,validators=[MinValueValidator(0)])
    remaining_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,editable=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Purchase Item" 
        verbose_name_plural = "Purchase Items"
        indexes = [
            models.Index(fields=['product_name']),
            models.Index(fields=['imei']),
        ]
        

    def clean(self):
        # Convert empty IMEI to None for uniqueness
        if self.imei == "":
            self.imei = None
            
        # Ensure paid amount doesn't exceed total
        if self.paid_amount and self.total_price and self.paid_amount > self.total_price:
            raise ValidationError("Paid amount cannot exceed total price")

    def save(self, *args, **kwargs):
        # Calculate financial fields
        self.total_price = Decimal(self.quantity) * Decimal(self.price)
        self.remaining_amount = max(
            self.total_price - (self.paid_amount or Decimal('0.00')), 
            Decimal('0.00')
        )
        super().save(*args, **kwargs)
        # Note: Voucher totals updated via signal, not direct save call

    def __str__(self):
        return f"{self.product_name} (Voucher: {self.voucher.voucher_number})"
        
        
class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="products") 
    name = models.CharField(max_length=191, null=False, blank=False, verbose_name="Product Name")
    description = models.TextField(max_length=191,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=False, blank=False,verbose_name="Product Price",db_index=True)
    warranty = models.IntegerField(null=True, blank=True)
    model_number = models.CharField(max_length=100,null=True, blank=True)
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


    def __str__(self):
        return self.name
    
    
class SalesVoucher(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    voucher_number = models.CharField(max_length=50, unique=True, editable=False)
    customer_name = models.CharField(max_length=191, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH)
    payment_status = models.CharField(max_length=20,choices=PaymentStatusChoices.choices,default=PaymentStatusChoices.PENDING)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sales Voucher"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['voucher_number']),
            models.Index(fields=['date']),
        ]

    def save(self, *args, **kwargs):
        # Generate voucher number
        if not self.voucher_number:
            prefix = "SV"
            with transaction.atomic():
                last_voucher = SalesVoucher.objects.select_for_update() \
                    .filter(voucher_number__startswith=prefix) \
                    .order_by('-voucher_number').first()
                if last_voucher:
                    last_num = int(last_voucher.voucher_number[len(prefix):])
                    self.voucher_number = f"{prefix}{last_num + 1:06d}"
                else:
                    self.voucher_number = f"{prefix}000001"
        
        # Calculate totals from items
        items = self.items.all()
        if items.exists():
            self.total_amount = sum(item.total_price for item in items)
        
        # Calculate financials
        net_total = self.total_amount - self.discount
        self.remaining_amount = net_total - self.paid_amount
        
        # Update payment status
        if self.remaining_amount <= 0:
            self.payment_status = PaymentStatusChoices.FULL_PAYMENT
        elif self.paid_amount > 0:
            self.payment_status = PaymentStatusChoices.PARTIAL_PAYMENT
        else:
            self.payment_status = PaymentStatusChoices.PENDING
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sales Voucher {self.voucher_number}"


class SalesItem(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('needs_repair', 'Needs Repair'),
    ]

    voucher = models.ForeignKey(SalesVoucher,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="sales_items")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=12,decimal_places=2,default=0.00,editable=False)
    warranty = models.IntegerField(null=True, blank=True)
    condition = models.CharField(max_length=20,choices=CONDITION_CHOICES,default='new')
    imei = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sales Item"
        verbose_name_plural = "Sales Items"
        indexes = [
            models.Index(fields=['imei']),
        ]

    def clean(self):
        if self.imei == "":
            self.imei = None
            
        # Set warranty from product if not specified
        if self.warranty is None and self.product.warranty:
            self.warranty = self.product.warranty

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)
        # Update parent voucher totals
        self.voucher.save()

    def __str__(self):
        return f"{self.product.name} (Voucher: {self.voucher.voucher_number})"
 
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
    materials_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    labour_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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
    
    def save(self, *args, **kwargs):
        # Calculate materials cost from repair items
        materials_total = self.repair_items.aggregate(
            total=models.Sum('total_cost')
        )['total'] or Decimal('0.00')
        self.materials_cost = materials_total
        
        # Calculate total repair cost
        self.total_amount = self.materials_cost + self.labour_cost
        
        # Update payment amounts (existing logic)
        self.paid_amount = Decimal(self.paid_amount)
        self.discount_amount = Decimal(self.discount_amount or 0)
        
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
    materials_used = models.ManyToManyField(RepairItem, related_name='repair_details', blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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
        
    def save(self, *args, **kwargs):
        if self.materials_used.exists():
            self.cost = sum(item.total_cost for item in self.materials_used.all())
        super().save(*args, **kwargs)

    
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
    
class RepairItem(models.Model):
    """
    Tracks individual items/materials used in a repair
    """
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE, related_name='repair_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='repair_usage')
    quantity_used = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Repair Material"
        verbose_name_plural = "Repair Materials"
        indexes = [
            models.Index(fields=['repair', 'product']),
            models.Index(fields=['created_at']),
        ]
    
    def clean(self):
        # Validate sufficient stock exists
        if self.product and self.quantity_used:
            if self.product.stock < self.quantity_used:
                raise ValidationError(
                    f"Insufficient stock for {self.product.name}. "
                    f"Available: {self.product.stock}, Required: {self.quantity_used}"
                )
    
    def save(self, *args, **kwargs):
        # Get current product price as unit cost if not specified
        if not self.unit_cost and self.product:
            self.unit_cost = self.product.price
        
        # Calculate total cost
        self.total_cost = self.quantity_used * self.unit_cost
        
        # Deduct from stock
        if self.pk is None:  # New entry
            with transaction.atomic():
                product = Product.objects.select_for_update().get(pk=self.product.pk)
                if product.stock < self.quantity_used:
                    raise ValidationError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock}, Required: {self.quantity_used}"
                    )
                
                # Update product stock
                product.stock -= self.quantity_used
                product.save(update_fields=['stock'])
                
                # Create stock ledger entry
                StockLedger.create_entry(
                    product=self.product,
                    transaction_type='adjustment',
                    reference_id=self.repair.id,
                    reference_model='Repair',
                    quantity=-self.quantity_used,
                    unit_cost=self.unit_cost,
                    notes=f"Used in repair #{self.repair.id}",
                    created_by=None  # Pass appropriate user here
                )
                
                super().save(*args, **kwargs)
                
                # Update repair total cost
                self.repair.save(update_fields=['total_amount'])
        else:
            super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity_used} (Repair #{self.repair.id})"
 
class SalesInvoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    sales_voucher = models.ForeignKey(SalesVoucher, on_delete=models.SET_NULL, related_name="sales_invoices", null=True, blank=True)
    # Store product info directly instead of relying on relations
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    warranty = models.IntegerField(null=True, blank=True)
    
    # Customer information
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_number = models.CharField(max_length=20, null=True, blank=True)  # Changed to CharField
    customer_address = models.TextField(null=True, blank=True)
    
    # Financial fields - all DecimalField for consistency
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    
    # Payment information
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.CASH)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.PENDING)
    
    # Additional fields
    due_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sales Invoice"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['created_at']),
        ]
    
    def clean(self):
        # Validate discount doesn't exceed subtotal
        subtotal = Decimal(self.quantity) * Decimal(self.unit_price or 0)
        if self.discount_amount > subtotal:
            raise ValidationError("Discount amount cannot exceed subtotal")
        
        # Validate paid amount doesn't exceed total
        total = subtotal - self.discount_amount
        if self.paid_amount > total:
            raise ValidationError("Paid amount cannot exceed total amount")
    
    def save(self, *args, **kwargs):
        # Generate invoice number
        if not self.invoice_number:
            with transaction.atomic():
                last_invoice = SalesInvoice.objects.select_for_update().filter(
                    invoice_number__startswith="SINV"
                ).order_by('-invoice_number').first()
                
                if last_invoice:
                    try:
                        last_num = int(last_invoice.invoice_number[4:])  # Remove "SINV" prefix
                        self.invoice_number = f"SINV{last_num + 1:06d}"
                    except (ValueError, IndexError):
                        self.invoice_number = "SINV000001"
                else:
                    self.invoice_number = "SINV000001"
        
        # Calculate financial fields
        self.subtotal = Decimal(self.quantity) * Decimal(self.unit_price or 0)
        self.discount_amount = min(self.discount_amount or Decimal('0.00'), self.subtotal)
        self.total_amount = self.subtotal - self.discount_amount
        self.remaining_amount = self.total_amount - (self.paid_amount or Decimal('0.00'))
        
        # Update payment status
        if self.remaining_amount <= 0:
            self.payment_status = PaymentStatusChoices.FULL_PAYMENT
            self.remaining_amount = Decimal('0.00')
        elif self.paid_amount > 0:
            self.payment_status = PaymentStatusChoices.PARTIAL_PAYMENT
        else:
            self.payment_status = PaymentStatusChoices.PENDING
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Sales Invoice {self.invoice_number} - {self.customer_name or 'No Customer'}"


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
    
    def clean(self):
        if self.quantity == 0:
            raise ValidationError("Quantity cannot be zero")
        if self.unit_cost < 0:
            raise ValidationError("Unit cost cannot be negative")
    
    @classmethod
    def create_entry(cls, product, transaction_type, reference_id, reference_model, 
                    quantity, unit_cost, created_by=None, notes=None):
        """
        Thread-safe method to create stock ledger entry
        """
        with transaction.atomic():
            # Lock the product to prevent concurrent stock updates
            product = Product.objects.select_for_update().get(pk=product.pk)
            
            # Get the latest balance for this product
            latest_entry = cls.objects.filter(product=product).first()
            
            # Calculate new values
            total_value = Decimal(quantity) * Decimal(unit_cost)
            
            if latest_entry:
                new_balance_qty = latest_entry.balance_quantity + quantity
                new_balance_value = latest_entry.balance_value + total_value
            else:
                new_balance_qty = quantity
                new_balance_value = total_value
            
            # Validate stock won't go negative
            if new_balance_qty < 0:
                raise ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {latest_entry.balance_quantity if latest_entry else 0}, "
                    f"Requested: {abs(quantity)}"
                )
            
            # Create the entry
            entry = cls.objects.create(
                product=product,
                transaction_type=transaction_type,
                reference_id=reference_id,
                reference_model=reference_model,
                quantity=quantity,
                unit_cost=unit_cost,
                total_value=total_value,
                balance_quantity=new_balance_qty,
                balance_value=new_balance_value,
                created_by=created_by,
                notes=notes
            )
            
            # Update product stock
            product.stock = new_balance_qty
            product.save(update_fields=['stock'])
            
            return entry
    
    def save(self, *args, **kwargs):
        # This should not be called directly - use create_entry instead
        if not self.pk:
            raise ValidationError("Use StockLedger.create_entry() method instead of direct save()")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.get_transaction_type_display()} - {self.quantity} units"


        
        
class Report(models.Model):
    total_sales = models.IntegerField(null=True, blank=True, db_index=True)
    total_purchases = models.IntegerField(null=True, blank=True, db_index=True)
    total_stock = models.IntegerField(null=True, blank=True, db_index=True)
    low_stock_count = models.IntegerField(null=True, blank=True, db_index=True)
    empty_stock_count = models.IntegerField(null=True, blank=True, db_index=True)
    total_stock_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Report"
        ordering = ['-created_at']
    
    @classmethod
    def generate_report(cls):
        """
        Generate a new report with current data
        """
        # Use efficient aggregation queries
        stock_data = Product.objects.aggregate(
            total_stock=models.Sum('stock'),
            low_stock=models.Count('id', filter=models.Q(stock__lte=5, stock__gt=0)),
            empty_stock=models.Count('id', filter=models.Q(stock=0)),
            total_value=models.Sum(models.F('stock') * models.F('price'))
        )
        
        sales_count = SalesVoucher.objects.filter(status='completed').count()
        purchase_count = PurchaseVoucher.objects.filter(status='completed').count()
        
        return cls.objects.create(
            total_sales=sales_count,
            total_purchases=purchase_count,
            total_stock=stock_data['total_stock'] or 0,
            low_stock_count=stock_data['low_stock'] or 0,
            empty_stock_count=stock_data['empty_stock'] or 0,
            total_stock_value=stock_data['total_value'] or Decimal('0.00')
        )
    
    def save(self, *args, **kwargs):
        # Only allow updates, not automatic calculations on save
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Report - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


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
    reference_id = models.CharField(max_length=50)
    reference_model = models.CharField(max_length=50)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices)
    is_bank = models.BooleanField(default=False)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    cheque_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Balance fields
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    bank_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    
    class Meta:
        ordering = ['-transaction_date', '-date']
        verbose_name = "Cashbook Entry"
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['entry_type']),
            models.Index(fields=['is_bank']),
        ]
    
    @classmethod
    def create_entry(cls, entry_type, source_type, reference_id, reference_model,
                    description, amount, payment_method, transaction_date,
                    is_bank=False, bank_name=None, cheque_number=None,
                    recorded_by=None, notes=None):
        """
        Thread-safe method to create cashbook entry with proper balance calculation
        """
        with transaction.atomic():
            # Get the latest balances
            latest_entry = cls.objects.select_for_update().order_by('-transaction_date', '-id').first()
            
            if latest_entry:
                prev_cash = latest_entry.cash_balance
                prev_bank = latest_entry.bank_balance
            else:
                prev_cash = prev_bank = Decimal('0.00')
            
            # Calculate new balances
            if is_bank:
                new_cash = prev_cash
                if entry_type == 'receipt':
                    new_bank = prev_bank + amount
                else:
                    new_bank = prev_bank - amount
            else:
                new_bank = prev_bank
                if entry_type == 'receipt':
                    new_cash = prev_cash + amount
                else:
                    new_cash = prev_cash - amount
            
            # Validate balances don't go negative
            if new_cash < 0:
                raise ValidationError("Insufficient cash balance")
            if new_bank < 0:
                raise ValidationError("Insufficient bank balance")
            
            # Create entry
            entry = cls.objects.create(
                entry_type=entry_type,
                source_type=source_type,
                reference_id=reference_id,
                reference_model=reference_model,
                description=description,
                amount=amount,
                payment_method=payment_method,
                is_bank=is_bank,
                bank_name=bank_name,
                cheque_number=cheque_number,
                transaction_date=transaction_date,
                recorded_by=recorded_by,
                notes=notes,
                cash_balance=new_cash,
                bank_balance=new_bank
            )
            
            return entry
    
    def save(self, *args, **kwargs):
        # Prevent direct save - use create_entry method
        if not self.pk:
            raise ValidationError("Use Cashbook.create_entry() method instead of direct save()")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_date} - {self.get_entry_type_display()} - {self.amount}"
    
class AccountType(models.TextChoices):
    ASSET = 'asset', 'Asset'
    LIABILITY = 'liability', 'Liability'
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'
    CAPITAL = 'capital', 'Capital'
    SUNDRY_DEBTORS = 'sundry_debtors', 'Sundry Debtors'
    SUNDRY_CREDITORS = 'sundry_creditors', 'Sundry Creditors'
    CASH_IN_HAND = 'cash_in_hand', 'Cash-in-Hand'
    
    
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
            if self.end_date < self.start_date:  # Remove .date
                raise ValidationError("End date must be after start date.")
            self.get_revenue()
            self.get_expenses()
            self.get_gross_profit()
            self.get_net_profit()
            super().save(*args, **kwargs)  # Call super().save, not super().__init__
        except Exception as e:
            logger.error(f"Error saving ProfitAndLoss for {self.start_date} to {self.end_date}: {str(e)}")
            raise ValidationError(f"Failed to save profit and loss statement: {str(e)}")