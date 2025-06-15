from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin 
from django.contrib.admin import DateFieldListFilter

# Register your models here.
admin.site.site_title='Stock Garden'
admin.site.site_header='Welcome to Stock Garden !'
admin.site.index_title='Stock Garden Inventory Management System'


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
    
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display=('name','description','created_at',)
    
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
    list_display=('category','amount','description','payment_method','payment_status','updated_at','created_at')
    list_filter=('category','amount',)
    
    
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
    list_display = ('transaction_date', 'product', 'transaction_type', 'quantity', 'unit_cost', 'total_value', 'balance_quantity')
    search_fields = ('product__name', 'reference_id')
    list_filter = ('transaction_type', ('transaction_date', DateFieldListFilter))
    readonly_fields = ('total_value', 'balance_quantity', 'balance_value', 'created_by')
    autocomplete_fields = ('product',)
    date_hierarchy = 'transaction_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

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

class PLLineItemInline(admin.TabularInline):
    model = PLLineItem
    extra = 1
    fields = ('label', 'amount', 'calculation_method', 'is_contra', 'order')
    ordering = ('order',)
    show_change_link = True


class PLSectionInline(admin.StackedInline):
    model = PLSection
    extra = 1
    fields = ('title', 'section_type', 'is_income', 'show_subtotal', 'order', 'notes')
    ordering = ('order',)
    show_change_link = True


@admin.register(ProfitLossStatement)
class ProfitLossStatementAdmin(admin.ModelAdmin):
    list_display = ('title', 'period_type', 'start_date', 'end_date', 'status', 'net_profit', 'generated_at', 'generated_by')
    list_filter = ('status', 'period_type', 'start_date', 'end_date')
    search_fields = ('title', 'notes')
    date_hierarchy = 'end_date'
    inlines = [PLSectionInline]
    readonly_fields = ('generated_at', 'net_profit', 'operating_profit', 'gross_profit', 'total_revenue', 'total_cogs', 'total_expenses', 'calculation_data')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'period_type', 'start_date', 'end_date', 'status', 'generated_by', 'notes')
        }),
        ('Profit & Loss Summary', {
            'fields': ('total_revenue', 'total_cogs', 'gross_profit', 'total_expenses', 'operating_profit', 'net_profit')
        }),
        ('Metadata', {
            'fields': ('generated_at', 'calculation_data')
        }),
    )


@admin.register(PLSection)
class PLSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'statement', 'section_type', 'is_income', 'order')
    list_filter = ('section_type', 'statement__title')
    search_fields = ('title', 'notes', 'statement__title')
    ordering = ('statement', 'order')
    inlines = [PLLineItemInline]


@admin.register(PLLineItem)
class PLLineItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'section', 'amount', 'calculation_method', 'is_contra', 'order')
    list_filter = ('calculation_method', 'is_contra', 'section__title')
    search_fields = ('label', 'description', 'section__title')
    ordering = ('section', 'order')

