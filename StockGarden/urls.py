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
    path('repair_detail/create/', RepairDetailCreate,name='repair_detail_create'),
    path('repair_detail/<int:pk>/update/', RepairDetailUpdate,name='repair_detail_update'),
    path('repair_detail/<int:pk>/delete/', RepairDetailDelete,name='repair_detail_delete'),
    
    path('expense/', ExpenseList, name='expense'),
    path('expense/create/', ExpenseCreate,name='expense_create'),
    path('expense/<int:pk>/update/', ExpenseUpdate,name='expense_update'),
    path('expense/<int:pk>/delete/', ExpenseDelete,name='expense_delete'),
    
    path('invoice/', SalesInvoiceList, name='invoice'),
    path('invoice/<int:pk>/update/', SalesInvoiceUpdate,name='invoice_update'),
    
    path('repair/', RepairInvoice, name='repair'),
    path('invoice/<int:pk>/update/', RepairUpdate,name='repair_update'),
    
    path('return/', ReturnList, name='return'),
    path('return/create/', ReturnCreate,name='return_create'),
    path('return/<int:pk>/update/', ReturnUpdate,name='return_update'),
    path('return/<int:pk>/delete/', ReturnDelete,name='return_delete'),


    
    path('user_report/', UserReportList, name='user_report'),
    path('sales_report/', SalesReportList, name='sales_report'),
    path('repair_report/', RepairReportList, name='repair_report'),
    path('stock_report/', StockReportList, name='stock_report'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
    path('generate_excel/', generate_excel, name='generate_excel'),

    
    path('search/', global_search, name='global_search'),

    path('sales-report/', SalesReportList, name='sales_report'),

    path('repair_report/', RepairReportList, name='repair_report'),

    path('repair_detail_report/', RepairDetailReportList, name='repair_detail_report'),
    path('chart-data/', get_chart_data, name='chart_data'),


    path("get-product-price/", get_product_price, name="get_product_price"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
