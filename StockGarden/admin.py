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
    
@admin.register(PurchaseVoucher)
class PurchaseVoucherAdmin(admin.ModelAdmin):
    list_display = (
        'voucher_number', 'date', 'vendor', 'total_amount',
        'discount', 'cost', 'payment_status', 'status'
    )
    list_filter = ('status', 'payment_status', 'date', 'vendor')
    search_fields = ('voucher_number', 'vendor__username')
    readonly_fields = ('voucher_number', 'total_amount', 'cost')
    fields = (
        'voucher_number', 'date', 'vendor', 'total_amount',
        'discount', 'cost', 'payment_method', 'payment_status', 'status'
    )
    ordering = ('-date',)
    
@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        'product_name', 'voucher', 'brand', 'category',
        'quantity', 'price', 'total_price', 'paid_amount',
        'remaining_amount'
    )
    list_filter = ('brand', 'category', 'condition')
    search_fields = ('product_name', 'imei', 'voucher__voucher_number')
    readonly_fields = ('total_price', 'remaining_amount')
    fields = (
        'voucher', 'brand', 'category', 'product_name',
        'warranty', 'condition', 'description', 'imei',
        'image', 'quantity', 'price', 'total_price',
        'paid_amount', 'remaining_amount'
    )
    
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin): 
    list_display = ('name','description','price','warranty', 'Imei', 'image','categories', 'stock','brand','created_at',)
    list_per_page=10
    search_fields = ('name','price',)
    list_filter = ('categories', 'brand','price','stock',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(SalesVoucher)
class SalesVoucherAdmin(admin.ModelAdmin):
    list_display = (
        'voucher_number', 'date', 'customer', 'total_amount',
        'discount', 'paid_amount', 'remaining_amount',
        'payment_status', 'status'
    )
    list_filter = ('status', 'payment_status', 'date', 'customer')
    search_fields = ('voucher_number', 'customer__username')
    readonly_fields = (
        'voucher_number', 'total_amount', 'remaining_amount'
    )
    fields = (
        'voucher_number', 'date', 'customer', 'total_amount',
        'discount', 'paid_amount', 'remaining_amount',
        'payment_method', 'payment_status', 'status'
    )
    ordering = ('-date',)
    
@admin.register(SalesItem)
class SalesItemAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'voucher', 'quantity', 'price', 'total_price',
        'warranty', 'condition', 'imei', 'created_at'
    )
    list_filter = ('condition', 'created_at', 'product')
    search_fields = ('product__name', 'voucher__voucher_number', 'imei')
    readonly_fields = ('total_price', 'created_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('product', 'voucher')
    fieldsets = (
        (None, {
            'fields': (
                'voucher', 'product', 'quantity', 'price', 'total_price',
                'warranty', 'condition', 'imei'
            )
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at',)
        }),
    )
     
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
    list_display=('invoice_number','customer_name','product_name','customer_number','customer_address','payment_method','discount_amount','subtotal','total_amount','payment_status','due_date','created_at')
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
    list_display = ('total_sales','total_purchases','total_stock','low_stock_count','empty_stock_count','total_stock_value','created_at','updated_at')

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

