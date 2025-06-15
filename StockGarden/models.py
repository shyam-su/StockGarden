from django.db import models
from user.models import User
from django.utils.text import slugify
import uuid
from decimal import Decimal
from PIL import Image
from django.db.models import Sum, Q


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
     
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=191, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Expense Category"
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
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices, default='cash',db_index=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='Pending',db_index=True,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Expense"


    def __str__(self):
        return f"{self.category.name if self.category else 'Uncategorized'} - {self.amount} ({self.payment_status})"

 
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
    reference_id = models.CharField(max_length=50)  # ID of the related transaction (purchase, sale, etc.)
    reference_model = models.CharField(max_length=50)  # Model name (e.g., 'Purchase', 'Sales')
    quantity = models.IntegerField()  # Positive for incoming, negative for outgoing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Cost per unit at time of transaction
    total_value = models.DecimalField(max_digits=12, decimal_places=2)  # quantity * unit_cost
    balance_quantity = models.IntegerField()  # Running balance
    balance_value = models.DecimalField(max_digits=12, decimal_places=2)  # Running total value
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Stock Ledger Entry"
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['product']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['reference_id']),
        ]
    
    def __str__(self):
        return f"{self.transaction_date.strftime('%Y-%m-%d')} - {self.product.name} - {self.get_transaction_type_display()} - Qty: {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate total value
        self.total_value = self.quantity * self.unit_cost
        
        # Get previous balance for this product
        previous_entry = StockLedger.objects.filter(
            product=self.product,
            transaction_date__lte=self.transaction_date
        ).exclude(id=self.id).order_by('-transaction_date', '-id').first()
        
        # Calculate running balances
        if previous_entry:
            self.balance_quantity = previous_entry.balance_quantity + self.quantity
            self.balance_value = previous_entry.balance_value + self.total_value
        else:
            self.balance_quantity = self.quantity
            self.balance_value = self.total_value
        
        super().save(*args, **kwargs)
        
        # Update product stock
        product = self.product
        product.stock = self.balance_quantity
        product.save()
        
        
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
        

class ProfitLossStatement(models.Model):
    """Official Profit & Loss Statement record with enhanced calculations"""
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('final', 'Final'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    calculation_data = models.JSONField(default=dict, blank=True)
    
    # Summary fields (auto-calculated)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_cogs = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Cost of Goods Sold
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    operating_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-end_date']
        verbose_name = "Profit & Loss Statement"
        verbose_name_plural = "Profit & Loss Statements"
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_after_start_date'
            )
        ]
    
    def __str__(self):
        return f"P&L Statement: {self.title} ({self.start_date} to {self.end_date})"
    
    def calculate_profit_loss(self):
        """
        Calculate all profit/loss metrics based on transactions between start and end dates
        """
        from django.db.models import Sum, Q
        
        # 1. Calculate Total Revenue (from Sales)
        sales_data = Sales.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        ).aggregate(
            total=Sum('total_amount'),
            paid=Sum('paid_amount')
        )
        self.total_revenue = sales_data['total'] or Decimal('0.00')
        
        # 2. Calculate Cost of Goods Sold (from Purchases)
        purchase_data = Purchase.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        ).aggregate(
            total=Sum('total_price')
        )
        self.total_cogs = purchase_data['total'] or Decimal('0.00')
        
        # 3. Calculate Gross Profit
        self.gross_profit = self.total_revenue - self.total_cogs
        
        # 4. Calculate Total Expenses
        expense_data = Expense.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        ).aggregate(
            total=Sum('amount')
        )
        self.total_expenses = expense_data['total'] or Decimal('0.00')
        
        # 5. Calculate Operating Profit
        self.operating_profit = self.gross_profit - self.total_expenses
        
        # 6. Calculate Net Profit (for now same as operating profit, can add taxes etc later)
        self.net_profit = self.operating_profit
        
        # Store detailed calculation data
        self.calculation_data = {
            'revenue_sources': self.get_revenue_breakdown(),
            'expense_breakdown': self.get_expense_breakdown(),
            'cogs_details': self.get_cogs_details(),
        }
        
        self.save()
    
    def get_revenue_breakdown(self):
        """Break down revenue by product category"""
        from django.db.models import Sum
        return Sales.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        ).values(
            'product__categories__name'
        ).annotate(
            total=Sum('total_amount')
        ).order_by('-total')
    
    def get_expense_breakdown(self):
        """Break down expenses by category"""
        from django.db.models import Sum
        return Expense.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        ).values(
            'category__name'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
    
    def get_cogs_details(self):
        """Break down cost of goods sold by product category"""
        return Purchase.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        ).values(
            'categories__name'
        ).annotate(
            total=Sum('total_price')
        ).order_by('-total')
    
    def save(self, *args, **kwargs):
        """Ensure dates are valid and calculations are done when finalizing"""
        if self.status == 'final' and not self.calculation_data:
            self.calculate_profit_loss()
        super().save(*args, **kwargs)
    
    def publish(self):
        """Mark statement as published"""
        if self.status != 'final':
            self.calculate_profit_loss()
        self.status = 'published'
        self.save()


class PLSection(models.Model):
    """Organized sections within a P&L statement with enhanced functionality"""
    SECTION_TYPES = [
        ('revenue', 'Revenue'),
        ('cogs', 'Cost of Goods Sold'),
        ('expense', 'Operating Expenses'),
        ('other_income', 'Other Income'),
        ('other_expense', 'Other Expenses'),
        ('tax', 'Taxes'),
    ]
    
    statement = models.ForeignKey(
        ProfitLossStatement, 
        on_delete=models.CASCADE, 
        related_name='sections'
    )
    title = models.CharField(max_length=100)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    order = models.PositiveIntegerField(default=0)
    is_income = models.BooleanField(default=True)
    show_subtotal = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "P&L Section"
        unique_together = ('statement', 'order')
    
    def __str__(self):
        return f"{self.title} ({self.statement})"
    
    @property
    def total_amount(self):
        """Calculate total for this section"""
        return self.line_items.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')


class PLLineItem(models.Model):
    """Detailed line items with calculation methods"""
    CALCULATION_METHODS = [
        ('auto', 'Automatic from Transactions'),
        ('manual', 'Manual Entry'),
        ('formula', 'Calculated Formula'),
    ]
    
    section = models.ForeignKey(
        PLSection, 
        on_delete=models.CASCADE, 
        related_name='line_items'
    )
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    calculation_method = models.CharField(
        max_length=20, 
        choices=CALCULATION_METHODS, 
        default='manual'
    )
    calculation_query = models.JSONField(blank=True, null=True)  # For auto-calculated items
    formula = models.CharField(max_length=200, blank=True)  # For formula-based items
    order = models.PositiveIntegerField(default=0)
    is_contra = models.BooleanField(
        default=False,
        help_text="Whether this item reduces the section total (like discounts)"
    )
    
    class Meta:
        ordering = ['order']
        verbose_name = "P&L Line Item"
    
    def __str__(self):
        return f"{self.label}: {self.amount}"
    
    def calculate_amount(self):
        """Calculate amount based on the calculation method"""
        if self.calculation_method == 'auto' and self.calculation_query:
            model = apps.get_model(self.calculation_query['model'])
            queryset = model.objects.filter(
                created_at__date__gte=self.section.statement.start_date,
                created_at__date__lte=self.section.statement.end_date
            )
            
            if 'filters' in self.calculation_query:
                queryset = queryset.filter(**self.calculation_query['filters'])
            
            result = queryset.aggregate(
                total=Sum(self.calculation_query['field'])
            )
            self.amount = result['total'] or Decimal('0.00')
        
        elif self.calculation_method == 'formula' and self.formula:
            # Implement formula calculation logic here
            # This would need to parse the formula and evaluate it
            pass
        
        self.save()