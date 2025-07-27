from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin 
from django.contrib.admin import DateFieldListFilter
from django.contrib import messages
import logging
from django.db import transaction



# Register your models here.
admin.site.site_title='Stock Garden'
admin.site.site_header='Welcome to Stock Garden !'
admin.site.index_title='Stock Garden Inventory Management System'

logger = logging.getLogger(__name__)
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display=('name','email','address','phone_number','reg_no','logo',)
    
@admin.register(Brand)
class BrandAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','created_at',)
    search_fields = ('name',)
    
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','created_at',)
    
    
@admin.register(Purchase)
class PurchaseAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('vendor','brand','categories','product_name','warranty','description','Imei','image','price','quantity','total_price','paid_amount','payment_method','payment_status','remaining_amount','created_at',)
    search_fields = ('vendor',)
    
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin): 
    list_display = ('name','description','price','warranty', 'Imei', 'image','categories', 'stock','brand','created_at',)
    list_per_page=10
    search_fields = ('name','price',)
    list_filter = ('categories', 'brand','price','stock',)

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'price', 'total_amount', 'payment_status', 'created_at')
    search_fields = ('user__full_name', 'product__name', 'Imei')
    list_filter = ('payment_status', 'payment_method', ('created_at', DateFieldListFilter))
    readonly_fields = ('total_amount', 'remaining_amount', 'created_at', 'updated_at')
    autocomplete_fields = ('user', 'product')
    
    def save_model(self, request, obj, form, change):
        # Ensure price is set from product if not provided
        if not obj.price and obj.product:
            obj.price = obj.product.price
        super().save_model(request, obj, form, change)
     
@admin.register(Repair)
class RepairOrderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('user','product_name','device_model','issue_description','payment_method','payment_status','total_amount','paid_amount','remaining_amount','status','out_date')
    list_filter=('product_name','device_model','status',)
    
@admin.register(RepairDetail)   
class RepairDetailAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('repair_order','repair_cost','repair_detail_cost','repair_action','created_at')
    list_filter=('repair_order','repair_action',)
    

@admin.register(Expense)
class ExpenseAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('category_type','amount','description','payment_method','payment_status','updated_at','created_at')
    list_filter=('category_type','amount',)
    
    
@admin.register(SalesInvoice)
class SalesInvoiceAdmin(ImportExportModelAdmin, admin.ModelAdmin):  
    list_display=('invoice_number','sales','customer_name','product_name','customer_number','customer_address','payment_method','discount_amount','subtotal','total_amount','payment_status','due_date','created_at')
    list_filter=('invoice_number','customer_name',)
    
@admin.register(RepairInvoice)
class RepairInvoiceAdmin(ImportExportModelAdmin, admin.ModelAdmin):  
    list_display=('invoice_number','customer_name','product_name','customer_number','customer_address','payment_method','discount_amount','total_amount','payment_status','due_date','created_at')
    list_filter=('invoice_number','customer_name',)
    
@admin.register(Return)
class ReturnAdmin(ImportExportModelAdmin, admin.ModelAdmin):  
    list_display=('invoice','product','quantity_returned','reason','return_date','total_amount','refund_amount','created_at')
    list_filter=('invoice','product',)

@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_date', 'transaction_type', 
                   'quantity', 'unit_cost', 'balance_quantity')
    list_filter = ('transaction_type', 'product')
    search_fields = ('product__name', 'reference_id')
    readonly_fields = ('balance_quantity', 'balance_value', 'total_value')
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'transaction_type', 'transaction_date')
        }),
        ('Transaction Details', {
            'fields': ('reference_id', 'reference_model', 'quantity', 'unit_cost')
        }),
        ('Calculated Fields', {
            'fields': ('total_value', 'balance_quantity', 'balance_value')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_by')
        }),
    )
    def get_readonly_fields(self, request, obj=None):
        # Make transaction_date read-only when editing existing records
        if obj:  # obj is None when creating a new record
            return ('transaction_date',) + self.readonly_fields
        return self.readonly_fields

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=('Total_sells','Total_purchase','Total_Stock','Low_Stock','Empty_Stock','created_at','updated_at',)
    list_filter = ('Total_sells', 'Total_purchase','Low_Stock',)

@admin.register(Daybook)
class DaybookAdmin(admin.ModelAdmin):
    list_display = ('date', 'transaction_type', 'description', 'debit_amount', 'credit_amount', 'balance')
    list_filter = ('transaction_type', 'date', 'payment_method')
    search_fields = ('description', 'reference_id')
    readonly_fields = ('date', 'transaction_type', 'reference_id', 'description', 
                      'debit_amount', 'credit_amount', 'balance')
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False  # Prevent manual addition since entries are created via signals
    

@admin.register(Cashbook)
class CashbookAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'entry_type', 'description', 'amount', 
                   'payment_method', 'is_bank', 'cash_balance', 'bank_balance')
    list_filter = ('entry_type', 'transaction_date', 'payment_method', 'is_bank')
    search_fields = ('description', 'reference_id')
    readonly_fields = ('cash_balance', 'bank_balance', 'date')
    date_hierarchy = 'transaction_date'
    fieldsets = (
        (None, {
            'fields': ('entry_type', 'source_type', 'reference_id', 'description')
        }),
        ('Financial Details', {
            'fields': ('amount', 'payment_method', 'is_bank', 'bank_name', 'cheque_number')
        }),
        ('Balances', {
            'fields': ('cash_balance', 'bank_balance')
        }),
        ('Dates', {
            'fields': ('transaction_date', 'date')
        }),
    )

