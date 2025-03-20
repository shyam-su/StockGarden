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
    
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','description','created_at',)
    
@admin.register(Purchase)
class PurchaseAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('vendor','brand','categories','product_name','description','Imei','image','price','quantity','remaining_amount','created_at',)
    search_fields = ('vendor',)
    
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin): 
    list_display = ('name', 'description','price', 'Imei', 'image','categories', 'stock','brand','created_at',)
    list_per_page=10
    search_fields = ('name','price',)
    list_filter = ('categories', 'brand','price','stock',)

@admin.register(Sales)
class SalesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','product','quantity','price','discount','payment_method','total_amount','paid_amount','remaining_amount','due_date','notes','expiring_date','updated_at','created_at',)
    search_fields = ('name',)
     
@admin.register(Repair)
class RepairOrderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('product_name','device_model','issue_description','created_at','out_date','status')
    list_filter=('product_name','device_model','status',)
    
@admin.register(RepairDetail)
class RepairDetailAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('repair_order','repair_cost','repair_action','created_at')
    list_filter=('repair_order','repair_action',)
    

@admin.register(Expense)
class ExpenseAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('category','amount','description','payment_method','payment_status','updated_at','created_at')
    list_filter=('category','amount',)
    
    
@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin, admin.ModelAdmin):  
    list_display=('invoice_number','sales','customer_name','customer_email','customer_address','payment_method','subtotal','discount_amount','total_amount','payment_status','due_date','created_at')
    list_filter=('invoice_number','customer_name',)
    
@admin.register(Return)
class ReturnAdmin(ImportExportModelAdmin, admin.ModelAdmin):  
    list_display=('invoice','product','quantity_returned','reason','return_date','refund_amount','created_at')
    list_filter=('invoice','product',)
    

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=('Total_sells','Total_purchase','Total_Stock','Low_Stock','Empty_Stock','created_at','updated_at',)
    list_filter = ('Total_sells', 'Total_purchase','Low_Stock',)
