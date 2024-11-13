from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    
    path('brand/', BrandListView, name='brand'),
    path('Brand/create/', BrandCreateView,name='brand_create'),
    path('brand/<int:pk>/update/', BrandUpdateView,name='brand_update'),
    path('brand/<int:pk>/delete/', BrandDeleteView,name='brand_delete'),
    
    path('category/', CategoryListView, name='category'),
    path('category/create/', CategoryCreateView,name='category_create'),
    path('category/<int:pk>/update/', CategoryUpdateView,name='category_update'),
    path('category/<int:pk>/delete/', CategoryDeleteView,name='category_delete'),
    
    path('sales/', SalesListView, name='sales'),
    path('sales/create/', SalesCreateView,name='sales_create'),
    path('sales/<int:pk>/update/', SalesUpdateView,name='sales_update'),
    path('sales/<int:pk>/delete/', SalesDeleteView,name='sales_delete'),
    
    path('product/', ProductListView, name='product'),
    path('product/create/', ProductCreateView,name='product_create'),
    path('product/<int:pk>/update/', ProductUpdateView,name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView,name='product_delete'),
    
    path('vendor/', VendorListView, name='vendor'),
    path('vendor/create/', VendorCreateView,name='vendor_create'),
    path('vendor/<int:pk>/update/', VendorUpdateView,name='vendor_update'),
    path('vendor/<int:pk>/delete/', VendorDeleteView,name='vendor_delete'),
    
    path('purchase/', PurchaseListView, name='purchase'),
    path('purchase/create/', PurchaseCreateView,name='purchase_create'),
    path('purchase/<int:pk>/update/', PurchaseUpdateView,name='purchase_update'),
    path('purchase/<int:pk>/delete/', PurchaseDeleteView,name='purchase_delete'),
    
    path('repair/', RepairListView, name='repair'),
    path('repair/create/', RepairCreateView,name='repair_create'),
    path('repair/<int:pk>/update/', RepairUpdateView,name='repair_update'),
    path('repair/<int:pk>/delete/', RepairDeleteView,name='repair_delete'),
    
    path('repair_detail/', RepairDetailListView, name='repair_detail'),
    path('repair_detail/create/', RepairDetailCreateView,name='repair_detail_create'),
    path('repair_detail/<int:pk>/update/', RepairDetailUpdateView,name='repair_detail_update'),
    path('repair_detail/<int:pk>/delete/', RepairDetailDeleteView,name='repair_detail_delete'),
    
    path('invoice/', InvoiceListView, name='invoice'),
    path('invoice/create/', InvoiceCreateView,name='invoice_create'),
    path('invoice/<int:pk>/update/', InvoiceUpdateView,name='invoice_update'),
    path('invoice/<int:pk>/delete/', InvoiceDeleteView,name='invoice_delete'),
    
    path('report/', ReportListView, name='report'),
    path('report/create/', ReportCreateView,name='report_create'),
    path('report/<int:pk>/update/', ReportUpdateView,name='report_update'),
    path('report/<int:pk>/delete/', ReportDeleteView,name='report_delete'),
]
