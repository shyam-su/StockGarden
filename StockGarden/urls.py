from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


# purchase_voucher_list
# sales_voucher_list
urlpatterns = [
    path('', home, name='home'),
    
    path('brand/', BrandList, name='brand'),
    path('brand/create/', BrandCreate, name='brand_create'),
    path('brand/<int:pk>/update/', BrandUpdate,name='brand_update'),
    path('brand/<int:pk>/delete/', BrandDelete,name='brand_delete'),
    
    path('category/', CategoryList, name='category'),
    path('category/create/', CategoryCreate,name='category_create'),
    path('category/<int:pk>/update/', CategoryUpdate,name='category_update'),
    path('category/<int:pk>/delete/', CategoryDelete,name='category_delete'),
    
    path('product/', ProductList, name='product'),
    path('product/<int:pk>/update/', ProductUpdate,name='product_update'),
    path('product/<int:pk>/delete/', ProductDelete,name='product_delete'),
    
    
    
    path('purchase/', purchase_list, name='purchase_list'),
    path('purchase/create/', purchase_create, name='purchase_create'),
    path('purchase/<int:pk>/update/', purchase_update, name='purchase_update'),
    path('purchase/<int:pk>/delete/', purchase_delete, name='purchase_delete'),
    path('purchase/<int:pk>/detail/', purchase_detail, name='purchase_detail'),
    
    # Purchase Item Management URLs
    path('purchase/<int:voucher_pk>/items/', purchase_items_list, name='purchase_items_list'),
    path('purchase/<int:voucher_pk>/items/add/', purchase_item_create, name='purchase_item_create'),
    path('purchase/<int:voucher_pk>/items/<int:pk>/update/', purchase_item_update, name='purchase_item_update'),
    path('purchase/<int:voucher_pk>/items/<int:pk>/delete/', purchase_item_delete, name='purchase_item_delete'),
    
    # Purchase AJAX API endpoints
    path('api/purchase/<int:pk>/totals/', update_voucher_totals, name='update_voucher_totals'),
    path('api/vendors/search/', vendor_search, name='vendor_search'),
    path('api/brands/create/', create_brand_ajax, name='create_brand_ajax'),
    path('api/categories/create/', create_category_ajax, name='create_category_ajax'),
    
    # Purchase Reports
    path('purchase/reports/', purchase_reports, name='purchase_reports'),
    path('purchase/export/', purchase_export, name='purchase_export'),
    
    path('repair/', RepairList, name='repair'),
    path('repair/create/', RepairCreate,name='repair_create'),
    path('repair/<int:pk>/update/', RepairUpdate,name='repair_update'),
    path('repair/<int:pk>/delete/', RepairDelete,name='repair_delete'),
    
    path('repair_detail/', RepairDetailList, name='repair_detail'),
    path('repair_detail/<int:pk>/update/', RepairDetailUpdate,name='repair_detail_update'),
    path('repair_detail/<int:pk>/delete/', RepairDetailDelete,name='repair_detail_delete'),
    
    path('expense/', ExpenseList, name='expense'),
    path('expense/create/', ExpenseCreate,name='expense_create'),
    path('expense/<int:pk>/update/', ExpenseUpdate,name='expense_update'),
    path('expense/<int:pk>/delete/', ExpenseDelete,name='expense_delete'),
    
    path('stock_ledger/', stock_ledger_list, name='stock_ledger'),
    path('stock_ledger/create/', stock_ledger_create, name='stock_ledger_create'),
    path('stock_ledger/update/<int:pk>/', stock_ledger_update, name='stock_ledger_update'),
    path('stock_ledger/delete/<int:pk>/', stock_ledger_delete, name='stock_ledger_delete'),
    
        # Sales Voucher URLs - Updated with voucher system
    path('sales/', sales_list, name='sales_list'),  # Alternative name for consistency
    path('sales/create/', sales_create, name='sales_create'),
    path('sales/<int:pk>/update/', sales_update, name='sales_update'),
    path('sales/<int:pk>/delete/', sales_delete, name='sales_delete'),
    path('sales/<int:pk>/detail/', sales_detail, name='sales_detail'),
    
    # Sales Item Management URLs
    path('sales/<int:voucher_pk>/items/', sales_items_list, name='sales_items_list'),
    path('sales/<int:voucher_pk>/items/add/', sales_item_create, name='sales_item_create'),
    path('sales/<int:voucher_pk>/items/<int:pk>/update/', sales_item_update, name='sales_item_update'),
    path('sales/<int:voucher_pk>/items/<int:pk>/delete/', sales_item_delete, name='sales_item_delete'),
    
    # Sales AJAX API endpoints
    path('api/sales/customers/search/', customer_search, name='customer_search'),
    path('api/sales/customers/create/', create_customer_ajax, name='create_customer_ajax'),
    path('api/sales/products/search/', product_search, name='product_search'),
    path('api/sales/products/<int:pk>/', get_product_details, name='get_product_details'),
    
    # Sales Reports
    path('sales/reports/', sales_reports, name='sales_reports'),
    path('sales/export/', sales_export, name='sales_export'),
    
    path('repairinvoice/', RepairInvoiceList, name='repairinvoice'),
    path('repairinvoice/<int:pk>/update/', RepairInvoiceUpdate,name='repairinvoice_update'),
    
    path('return/', ReturnList, name='return'),
    path('return/create/', ReturnCreate,name='return_create'),
    path('return/<int:pk>/update/', ReturnUpdate,name='return_update'),
    path('return/<int:pk>/delete/', ReturnDelete,name='return_delete'),

    path('salesinvoiceprint/<int:pk>/', generate_sales_invoice, name='salesinvoiceprint'),
    path('repairinvoiceprint/<int:pk>/', generate_repair_invoice, name='repairinvoiceprint'),

    path('user_report/', UserReportList, name='user_report'),
    path('sales_report/', SalesReportList, name='sales_report'),
    path('repair_report/', RepairReportList, name='repair_report'),
    path('repair_detail_report/', RepairDetailReportList, name='repair_detail_report'),
        
    
    path('daybook/', daybook_list, name='daybook_list'),
    path('daybook/create/', daybook_create, name='daybook_create'),
    path('daybook/update/<int:pk>/', daybook_update, name='daybook_update'),
    path('daybook/delete/<int:pk>/', daybook_delete, name='daybook_delete'),
    
    path('cashbook/', cashbook_list, name='cashbook_list'),
    path('cashbook/create/', cashbook_create, name='cashbook_create'),
    path('cashbook/update/<int:pk>/', cashbook_update, name='cashbook_update'),
    path('cashbook/delete/<int:pk>/', cashbook_delete, name='cashbook_delete'),
    
    path('stock_report/', StockReportList, name='stock_report'),
    path('stock_excel/', stock_excel, name='stock_excel'),
    path('sales_excel/', sales_excel, name='sales_excel'),
    path('search/', global_search, name='global_search'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
