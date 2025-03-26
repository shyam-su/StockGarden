from django.db import models
from user.models import User
from django.utils.text import slugify
import uuid
from decimal import Decimal
from PIL import Image

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
    name = models.CharField(max_length=191,)
    address = models.CharField(max_length=191)
    email = models.EmailField(max_length=191,db_index=True)
    phone_number = models.CharField(max_length=20,db_index=True)
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
    product_name = models.CharField(max_length=191, null=True, blank=True)
    warranty = models.IntegerField(null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    description = models.TextField(max_length=191, blank=True, null=True)
    Imei = models.CharField(max_length=100,unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='media/products_imgs/',null=True, blank=True)
    quantity = models.IntegerField()
    price = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) 
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Purchase"
        indexes = [models.Index(fields=['product_name',])]
        
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price 
        self.remaining_amount=self.total_price-self.paid_amount
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
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)  
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True) 
    Imei = models.CharField(max_length=100,unique=True, blank=True, null=True,db_index=True)
    warranty = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(blank=True, null=True)
    discount=models.IntegerField(null=True, blank=True, default=0)
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH,db_index=True)
    payment_status=models.CharField(max_length=191,choices=PaymentStatusChoices, default='Pending',db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    due_date = models.DateTimeField(null=True, blank=True) 
    notes = models.TextField(null=True, blank=True) 
    expiring_date = models.DateTimeField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True,verbose_name="Sale Date")
    updated_at=models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.price = self.product.price  
        self.warranty = self.product.warranty  
        self.total_amount = Decimal(self.quantity) * Decimal(self.price)
        self.paid_amount = Decimal(self.paid_amount)
        self.discount = Decimal(self.discount or 0) 
        self.remaining_amount = self.total_amount - self.paid_amount - self.discount
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
    payment_status=models.CharField(max_length=191,choices=PaymentStatusChoices, default='Pending',db_index=True)
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
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='pending',db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Expense"


    def __str__(self):
        return f"{self.category.name if self.category else 'Uncategorized'} - {self.amount} ({self.payment_status})"

 
class SalesInvoice(models.Model):
    invoice_number = models.CharField(max_length=6, unique=True, default=uuid.uuid4)
    sales = models.ForeignKey(Sales, on_delete=models.SET_NULL,related_name="salesinvoice", null=True, blank=True)  
    product_name = models.CharField(max_length=255)
    warranty = models.IntegerField(null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_number = models.IntegerField(null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.CASH,db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='pending',db_index=True)
    due_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        verbose_name = "Sales Invoice"
        indexes = [models.Index(fields=['invoice_number',])]
    
    def __str__(self):
        return f"Sales Invoice {self.invoice_number} for Sale {self.customer_name}"


class RepairInvoice(models.Model):
    invoice_number = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    repair = models.ForeignKey(Repair, on_delete=models.SET_NULL,related_name="repairinvoice", null=True, blank=True)  
    product_name = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    customer_number = models.IntegerField(null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.CASH,db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='pending',db_index=True)
    due_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Repair Invoice"
        indexes = [models.Index(fields=['invoice_number',])]
    
    def __str__(self):
        return f"Repair Invoice {self.invoice_number} for Sale {self.customer_name}"

class Return(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.SET_NULL,null=True,related_name="invoice")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="product") 
    quantity_returned = models.PositiveIntegerField()
    reason = models.TextField(null=True, blank=True)
    return_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product Return"
        indexes = [models.Index(fields=['return_date'])]
    
    def __str__(self):
        return f"Return for Invoice #{self.invoice.invoice_number} - Product {self.product.name}"
    
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
    