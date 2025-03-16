from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin 


# Register your models here.
admin.site.site_title='Stock Garden'
admin.site.site_header='Welcome to Stock Garden !'
admin.site.index_title='Stock Garden Inventory Management System'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display=('name','email','address','phone_number','logo',)
    
@admin.register(Brand)
class BrandAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','created_at',)
    search_fields = ('name',)
    
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','created_at',)
    
    
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin): 
    list_display = ('name', 'description','price', 'Imei', 'image','categories', 'stock','brand','created_at',)
    list_per_page=10
    search_fields = ('name','price',)
    list_filter = ('categories', 'brand','price','stock',)

@admin.register(Sales)
class SalesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','product','quantity','price','created_at',)
    search_fields = ('name',)
    
    
@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','email','address','contact_no','company_name','created_at',)
    
    
@admin.register(Purchase)
class PurchaseAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('vendor','product','quantity','price','created_at',)
    search_fields = ('vendor',)
    
@admin.register(Repair)
class RepairOrderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('product_name','device_model','issue_description','created_at','out_date','status')
    list_filter=('product_name','device_model','status',)
    
@admin.register(RepairDetail)
class RepairDetailAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('repair_order','repair_cost','repair_action','created_at')
    list_filter=('repair_order','repair_action',)

@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('sales','discount','payment_method','status','created_at','updated_at',)
    list_filter = ('payment_method', 'status',)
    
    
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=('Total_sells','Total_purchase','Total_Stock','Low_Stock','Empty_Stock','created_at','updated_at',)
    list_filter = ('Total_sells', 'Total_purchase','Low_Stock',)
