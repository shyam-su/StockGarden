from django.db import models
from user.models import User
from django.utils.text import slugify
import uuid
from django.db import transaction
from django.utils import timezone


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
    name = models.CharField(max_length=191,db_index=True)
    address = models.CharField(max_length=191)
    email = models.EmailField(max_length=191)
    phone_number = models.CharField(max_length=20,db_index=True)
    logo = models.ImageField(upload_to='company/logos/', blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
       
    
    class Meta:
        verbose_name = "Company"
        indexes = [models.Index(fields=['name','phone_number'])]
        
class Brand(models.Model):
    name=models.CharField(max_length=191,unique=True,verbose_name="Brand Name",db_index=True)
    image = models.ImageField(upload_to='media/brands_imgs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Brand"
        indexes = [models.Index(fields=['name'])]

    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=191,verbose_name="Category Name",unique=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Category"
        indexes = [models.Index(fields=['name'])]   

    def __str__(self):
        return self.name
     
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=191, unique=True, db_index=True)
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
    vendor = models.ForeignKey(User,on_delete=models.CASCADE)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True,db_index=True)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True,db_index=True)
    product_name = models.CharField(max_length=191, null=True, blank=True, db_index=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new', db_index=True)
    description = models.TextField(max_length=191, blank=True, null=True)
    Imei = models.CharField(max_length=100,unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='media/products_imgs/',null=True, blank=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Purchase"
        indexes = [models.Index(fields=['vendor', 'brand', 'categories', 'product_name',])]
        
        
class Product(models.Model):
    vendor= models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True,db_index=True)
    name = models.CharField(max_length=191,null=False, blank=False,verbose_name="Product Name",db_index=True)
    description = models.TextField(max_length=191,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=False, blank=False,verbose_name="Product Price",db_index=True)
    Imei = models.CharField(max_length=100,null=True, blank=True,db_index=True)
    image = models.ImageField(upload_to='media/products_imgs/',null=True, blank=True,db_index=True)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True,db_index=True)
    stock=models.IntegerField(null=True, blank=True,db_index=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True,db_index=True)
    slug = models.SlugField(max_length=191,null=True, blank=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product"
        indexes = [models.Index(fields=['name','description','price','image','categories','stock','brand'])]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            unique_id = str(uuid.uuid4())[:8]
            self.slug = slugify(f"{self.name}-{unique_id}")
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    

class Sales(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True,verbose_name="Party Name",db_index=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    Imei = models.CharField(max_length=100,unique=True, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    discount=models.IntegerField(null=True, blank=True, default=0)
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH)
    payment_status=models.CharField(max_length=191,choices=PaymentStatusChoices, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    due_date = models.DateTimeField(null=True, blank=True) 
    notes = models.TextField(null=True, blank=True) 
    expiring_date = models.DateTimeField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True,verbose_name="Sale Date")
    updated_at=models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        with transaction.atomic():
            if self.product and self.product.stock is not None:
                if self.quantity > self.product.stock:
                    raise ValueError("Not enough stock available.")
                self.product.stock -= self.quantity
                self.product.save()
            super(Sales, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Seller"
        indexes = [models.Index(fields=['name','product','price'])]

    def __str__(self):
       return f"{self.name} - {self.product} - Quantity: {self.quantity} - Price: {self.price}"


 
class Repair(models.Model):
    STATUS_CHOICES = [
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('pending', 'Pending Pickup'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True,verbose_name="Customer Name",db_index=True)
    product_name = models.CharField(max_length=100) 
    device_model = models.CharField(max_length=100)
    issue_description = models.TextField() 
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH)
    payment_status=models.CharField(max_length=191,choices=PaymentStatusChoices, default='Pending')
    notes = models.TextField(null=True, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in-progress')
    out_date = models.DateTimeField(null=True, blank=True) 
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Repair"
        indexes = [models.Index(fields=['product_name','device_model','status'])]
    
    def __str__(self):
        return f"{self.device_model} - {self.status} ({self.name})"
    
    
class RepairDetail(models.Model):
    STATUS_CHOICES = [
        ('in', 'In'),
        ('repairing', 'Repairing'),
        ('repaired', 'Repaired'),
        ('returned', 'Returned'),
    ]

    id = models.AutoField(primary_key=True)
    repair_order = models.ForeignKey(Repair, related_name='repair_details', on_delete=models.CASCADE,)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_description = models.TextField() 
    repair_action = models.CharField(choices=STATUS_CHOICES, max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Repair Detail"
        indexes = [models.Index(fields=['repair_order','repair_action'])]
    
    def __str__(self):
        return f"{self.repair_order.device_model}"

class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices, default='cash', db_index=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Expense"
        indexes = [
            models.Index(fields=['amount', 'payment_status']),
        ]

    def __str__(self):
        return f"{self.category.name if self.category else 'Uncategorized'} - {self.amount} ({self.payment_status})"

 
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(max_length=255)
    customer_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=20,choices=PaymentMethodChoices.choices,default=PaymentMethodChoices.CASH)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices, default='pending')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Invoice"
        indexes = [models.Index(fields=['invoice_number', 'due_date'])]


class Return(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
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
        indexes = [models.Index(fields=['Total_sells','Total_purchase','Total_Stock','Low_Stock','Empty_Stock'])]
    
    