from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


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
    
    path('sales/', SalesList, name='sales'),
    path('sales/create/', SalesCreate,name='sales_create'),
    path('sales/<int:pk>/update/', SalesUpdate,name='sales_update'),
    path('sales/<int:pk>/delete/', SalesDelete,name='sales_delete'),
    
    
    path('purchase/', PurchaseList, name='purchase'),
    path('purchase/create/', PurchaseCreate,name='purchase_create'),
    path('purchase/<int:pk>/update/', PurchaseUpdate,name='purchase_update'),
    path('purchase/<int:pk>/delete/', PurchaseDelete,name='purchase_delete'),
    
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
    
    path('salesinvoice/', SalesInvoiceList, name='salesinvoice'),
    path('salesinvoice/<int:pk>/update/', SalesInvoiceUpdate,name='salesinvoice_update'),
    
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
    
    path('accounts/', account_list, name='account_list'),
    path('accounts/create/', account_create, name='account_create'),
    path('accounts/<int:pk>/', account_detail, name='account_detail'),
    
    # Ledger Entry URLs
    path('ledger/entries/create/', ledger_entry_create, name='ledger_entry_create'),
    
    # Balance Sheet URLs
    path('reports/balance-sheets/', balance_sheet_list, name='balance_sheet_list'),
    path('reports/balance-sheets/<int:pk>/', balance_sheet_detail, name='balance_sheet_detail'),
    
    # Profit & Loss URLs
    path('reports/profit-loss/', profit_and_loss_list, name='profit_and_loss_list'),
    path('reports/profit-loss/<int:pk>/', profit_and_loss_detail, name='profit_and_loss_detail'),

    
    path('stock_report/', StockReportList, name='stock_report'),
    path('stock_excel/', stock_excel, name='stock_excel'),
    path('sales_excel/', sales_excel, name='sales_excel'),
    path('search/', global_search, name='global_search'),




]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
