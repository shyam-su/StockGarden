from django.db import models
from user.models import User
from django.utils.text import slugify
import uuid
from django.db import transaction



# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255,db_index=True)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=20,db_index=True)
    logo = models.ImageField(upload_to='company/logos/', blank=True)    
    
    class Meta:
        verbose_name = "Company"
        indexes = [models.Index(fields=['name','phone_number'])]
        
class Brand(models.Model):
    name=models.CharField(max_length=255,blank=False,null=False,verbose_name="Brand Name",db_index=True)
    image=models.ImageField(upload_to='media/brands_imgs/',null=True, blank=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    
    class Meta:
        verbose_name = "Brand"
        indexes = [models.Index(fields=['name'])]

    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255,null=True, blank=False ,verbose_name="Category Name",db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Category"
        indexes = [models.Index(fields=['name'])]   

    def __str__(self):
        return self.name
    
class Vendor(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True,verbose_name="Party Name",db_index=True)
    company_name = models.CharField(max_length=200, blank=True,verbose_name="Company Name")
    address = models.CharField(max_length=300,blank=False,null=False)
    contact_no = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Vendor"
        indexes = [models.Index(fields=['name','contact_no','company_name'])]
    

    def __str__(self):
        return self.company_name

class Product(models.Model):
    vendor= models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True, blank=True,db_index=True)
    name = models.CharField(max_length=255,null=False, blank=False,verbose_name="Product Name",db_index=True)
    description = models.TextField(max_length=255,null=True, blank=True,db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=False, blank=False,verbose_name="Product Price",db_index=True)
    Imei = models.CharField(max_length=100,null=True, blank=True,db_index=True)
    image = models.ImageField(upload_to='media/products_imgs/',null=True, blank=True,db_index=True)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True,db_index=True)
    stock=models.IntegerField(null=True, blank=True,db_index=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True,db_index=True)
    slug = models.SlugField(max_length=255,null=True, blank=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product"
        indexes = [models.Index(fields=['name','description','price','image','categories','stock','brand'])]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            while Product.objects.filter(slug=self.slug).exists(): 
                self.slug = f"{self.slug}-{str(uuid.uuid4())[:8]}"
        return super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return self.name
    

class Sales(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True,verbose_name="Party Name",db_index=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    total = models.IntegerField()
    contact_no = models.CharField(max_length=15,null=True, blank=True)
    expiring_date = models.DateTimeField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True,verbose_name="Sale Date")
    
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



class Purchase(models.Model):
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True, blank=True,db_index=True,default="No Available")
    description = models.TextField(max_length=300, blank=True, null=True)
    quantity = models.IntegerField()
    price = models.IntegerField()
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.total_value = self.quantity * self.price
        with transaction.atomic():
            super(Purchase, self).save(*args, **kwargs)
            if self.product:
                self.product.stock = (self.product.stock or 0) + self.quantity
                self.product.save()
    
    class Meta:
        ordering = ['id']
        verbose_name = "Purchase"
        indexes = [models.Index(fields=['product','vendor',])]
    
    def __str__(self):
     return f"{self.vendor} - {self.product} - Quantity: {self.quantity} - Price: {self.price}"
 
class Repair(models.Model):
    STATUS_CHOICES = [
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('pending', 'Pending Pickup'),
    ]

    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100) 
    device_model = models.CharField(max_length=100)
    name = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True,verbose_name="Customer Name",db_index=True)
    issue_description = models.TextField() 
    out_date = models.DateTimeField(null=True, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in-progress')
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

    
    class Meta:
        verbose_name = "Repair Detail"
        indexes = [models.Index(fields=['repair_order','repair_action'])]
    
    def __str__(self):
        return f"{self.repair_order.device_model}"


 

class Invoice(models.Model):
    Payment_Method = {
        ('Cash on Hands', 'Cash on Hands'),
        ('Khalti', 'Khalti'),
        ('Esewa', 'Esewa'),
        ('Bank Transfer', 'Bank Transfer'),
        
    }
    Status = {
        ('Full Payment', 'Full Payment'),
        ('Pending', 'Pending'),  
    }
    sales=models.ForeignKey(Sales,on_delete=models.CASCADE)
    discount=models.IntegerField(null=True, blank=True)
    payment_method=models.CharField(max_length=255,choices=Payment_Method ,db_index=True)
    status=models.CharField(max_length=255,choices=Status,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Invoice"
        indexes = [models.Index(fields=['sales','payment_method','status'])]

    def __str__(self):
        return f"{self.sales.quantity} x {self.sales.product}"
 
class Report(models.Model):
    Total_sells = models.IntegerField(null=True, blank=True,db_index=True)
    Total_purchase = models.IntegerField(null=True, blank=True,db_index=True)
    Total_Stock=models.IntegerField(null=True, blank=True,db_index=True)
    Low_Stock=models.IntegerField(null=True, blank=True,db_index=True)
    Empty_Stock=models.IntegerField(null=True, blank=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.total_stock = Product.objects.aggregate(total=models.Sum('stock'))['total'] or 0
        self.low_stock = Product.objects.filter(stock__lte=5).count()
        self.empty_stock = Product.objects.filter(stock=0).count()
        super(Report, self).save(*args, **kwargs)

    
    class Meta:
        verbose_name = "Report"
        indexes = [models.Index(fields=['Total_sells','Total_purchase','Total_Stock','Low_Stock','Empty_Stock'])]
    
    