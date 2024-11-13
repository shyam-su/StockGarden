from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display=('name','created_at',)
    search_fields = ('name',)
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name','created_at',)
    
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): 
    list_display = ('name', 'description','price', 'Imei', 'image','categories', 'stock','brand','created_at',)
    list_per_page=10
    search_fields = ('name','price',)
    list_filter = ('categories', 'brand','price','stock',)

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display=('name','product','quantity','price','created_at',)
    search_fields = ('name',)
    
    
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display=('name','email','address','contact_no','company_name','created_at',)
    
    
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display=('vendor','product','quantity','price','created_at',)
    search_fields = ('vendor',)
    
@admin.register(Repair)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display=('product_id','device_model','name','issue_description','in_date','out_date','status','notes',)
    list_filter=('product_id','device_model','name','status',)
    
@admin.register(RepairDetail)
class RepairDetailAdmin(admin.ModelAdmin):
    list_display=('repair_order','repair_cost','repair_action','action_date')
    list_filter=('repair_order','repair_action',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display=('product','price','quantity','total_price','payment_method','status','created_at','updated_at',)
    list_filter = ('payment_method', 'status',)
    
    
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=('Total_sells','Total_purchase','Total_Stock','Low_Stock','Empty_Stock','created_at','updated_at',)
    list_filter = ('Total_sells', 'Total_purchase','Low_Stock',)
