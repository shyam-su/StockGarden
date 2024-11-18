from django.shortcuts import render


# Create your views here
def home(request):
    return render(request, 'home.html',)

def BrandListView(request):
    return render(request, 'brand.html',)

def BrandCreateView(request):
    return render(request, 'brand_create.html',)

def BrandUpdateView(request):
    return render(request, 'brand_update.html',)

def BrandDeleteView(request):
    return render(request, 'brand_delete.html',)

def CategoryListView(request):
    return render(request, 'category.html',)

def CategoryCreateView(request):
    return render(request, 'category_create.html',)

def CategoryUpdateView(request):
    return render(request, 'category_update.html',)

def CategoryDeleteView(request):
    return render(request, 'category_delete.html',)

def ProductListView(request):
    return render(request, 'products.html',)

def ProductCreateView(request):
    return render(request, 'product_create.html',)

def ProductUpdateView(request):
    return render(request, 'product_update.html',)

def ProductDeleteView(request):
    return render(request, 'product_delete.html',)

def SalesListView(request):
    return render(request, 'sales.html',)

def SalesCreateView(request):
    return render(request, 'sale_create.html',)

def SalesUpdateView(request):
    return render(request, 'home.html',)

def SalesDeleteView(request):
    return render(request, 'sale_delete.html',)

def VendorListView(request):
    return render(request, 'vendor.html',)

def VendorCreateView(request):
    return render(request, 'vendor_create.html',)

def VendorUpdateView(request):
    return render(request, 'vendor_update.html',)

def VendorDeleteView(request):
    return render(request, 'vendor_delete.html',)

def PurchaseListView(request):
    return render(request, 'purchases.html',)

def PurchaseCreateView(request):
    return render(request, 'purchases_create.html',)

def PurchaseUpdateView(request):
    return render(request, 'home.html',)

def PurchaseDeleteView(request):
    return render(request, 'purchase_delete.html',)

def RepairListView(request):
    return render(request, 'repair.html',)

def RepairCreateView(request):
    return render(request, 'repair_create.html',)

def RepairUpdateView(request):
    return render(request, 'brand_update.html',)

def RepairDeleteView(request):
    return render(request, 'repair_delete.html',)

def RepairDetailListView(request):
    return render(request, 'repair_detail.html',)

def RepairDetailCreateView(request):
    return render(request, 'repair_detail_create.html',)

def RepairDetailUpdateView(request):
    return render(request, 'repair_detail_update.html',)

def RepairDetailDeleteView(request):
    return render(request, 'repair_detail_delete.html',)

def InvoiceListView(request):
    return render(request, 'invoice.html',)

def InvoiceCreateView(request):
    return render(request, 'invoice_create.html',)

def InvoiceUpdateView(request):
    return render(request, 'invoice_update.html',)

def InvoiceDeleteView(request):
    return render(request, 'invoice_delete.html',)

def ReportListView(request):
    return render(request, 'home.html',)

def ReportCreateView(request):
    return render(request, 'home.html',)

def ReportUpdateView(request):
    return render(request, 'home.html',)

def ReportDeleteView(request):
    return render(request, 'home.html',)