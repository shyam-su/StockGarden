from django.shortcuts import render
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
import logging
from django.core.paginator import Paginator
from django.contrib import messages  
import pickle as pk




# Create your views here
# Set up logging
logger = logging.getLogger(__name__)
def home(request):
    return render(request, 'home.html',)

def BrandListView(request):
    try:
        brands = Brand.objects.all()
        paginator = Paginator(brands, 10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"brand": page_obj}
        return render(request, 'brand.html', context)
    except Exception as e:
        logger.error(f"Error in BrandListView: {e}")
        # Add an error message if something goes wrong
        messages.error(request, 'An error occurred while loading the brand list.')

        return render(request, '404.html', {"message": "An error occurred."})


def BrandCreateView(request, brand_id=None):
    try:
        if brand_id:  # Check if we are updating an existing brand
            brand = get_object_or_404(Brand, id=brand_id)
            form = BrandForm(request.POST or None, instance=brand)
            action = "Update"
        else:  # Creating a new brand
            form = BrandForm(request.POST or None)
            action = "Create"

        if request.method == 'POST':
            if form.is_valid():
                form.save()  # Save the brand to the database
                messages.success(request, f'Brand {action.lower()}d successfully!')
                return redirect('brand')  # Redirect to the brand list view after successful creation/update

        return render(request, 'brand_create.html', {'form': form, 'action': action})

    except Exception as e:
        logger.error(f"Error in BrandCreateView: {e}")
        messages.error(request, 'An error occurred while processing the brand.')
        return render(request, '404.html', {"message": "An error occurred."})

def BrandUpdateView(request, pk):
    try:
        brand = get_object_or_404(Brand, pk=pk)

        if request.method == 'POST':
            form = BrandForm(request.POST, instance=brand)
            if form.is_valid():
                form.save()
                # Add a success message after updating
                messages.success(request, f"The brand '{brand.name}' has been successfully updated.")
                return redirect('brand')  # Redirect back to the brand list page after saving
        else:
            form = BrandForm(instance=brand)

        return render(request, 'brand_update.html', {'form': form, 'brand': brand})

    except Exception as e:
        logger.error(f"Error in BrandUpdateView for brand {pk}: {e}")
        messages.error(request, 'An error occurred while updating the brand.')
        return render(request, 'error.html', {"message": "An error occurred while updating the brand."})


def BrandDeleteView(request, pk):
    try:
        # Get the brand object or raise a 404 error if not found
        brand = get_object_or_404(Brand, pk=pk)

        if request.method == 'POST':
            brand_name = brand.name  # Store the brand name before deletion
            brand.delete()  # Delete the brand

            # Add a success message after deletion
            messages.success(request, f"The brand '{brand_name}' has been successfully deleted.")

            # Redirect to the brand list or another appropriate page
            return redirect('brand')  # Assuming 'brand_list' is the name of the URL pattern for the brand list page

        # If it's not a POST request, render the confirmation page for deletion
        return render(request, 'brand_delete.html', {'brand': brand})

    except Exception as e:
        # Log the error and display a friendly error message
        logger.error(f"Error in BrandDeleteView for brand {pk}: {e}")
        messages.error(request, 'An error occurred while deleting the brand.')
        
        # Redirect to a safe page instead of rendering a 404 error page
        return render(request, '404.html', {"message": "An error occurred while deleting the brand."}) # Redirect to the brand list page or an appropriate page for error handling


def CategoryListView(request):
    try:
        category =Category.objects.all()
        paginator =Paginator(category,10)
        page_number =request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        print(page_obj.object_list)
        
        context={
            "category":page_obj, 
        }
        return render(request,'category.html',context)
    except Exception as e:
        logger.error(f" Error in CategoryListView: {e}")
        return render(request, '404.html', {"message": "An error occurred."})

def CategoryCreateView(request,catagory_id=None):
    try:
        if catagory_id:
            category =get_object_or_404(Category,id=catagory_id)
            form = CategoryForm(request.POST or None,instance=category)
            action="Update"
        else:
            form = CategoryForm(request.POST or None)
            action="Create"
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request,f'Caregory {action.lower()}d successfully!')
                return redirect('category')
        return render(request, 'category_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in Category Create View: {e}")
        messages.error(request, 'An error occurred while processing the category.')
        return render(request, '404.html', {"message": "An error occurred."})
    
def CategoryUpdateView(request,pk):
    try:
        category=get_object_or_404(Category,pk=pk)
        if request.method == 'POST':
            form =CategoryForm(request.POST ,instance=category)
            if form.is_valid():
                form.save()
                messages.success(request,f'Category updated successfully!')
                return redirect('category')
        else:
            form =CategoryForm(instance=category)
        return render(request, 'category_update.html',{'form':form,'category':category})
    except Exception as e:
        logger.error(f"Error in CategoryUpdateView: {e}")
        messages.error(request, 'An error occurred while processing the category.')
        return render(request, '404.html', {"message": "An error occurred."})

def CategoryDeleteView(request,pk):
    try:
        category=get_object_or_404(Category,pk=pk)
        if request.method == 'POST':
            category_name=category.name
            category.delete()
            messages.success(request,f'Category {category_name} deleted successfully!')
            return redirect('category')
        
        return render(request, 'category_delete.html',{'category':category})
    except Exception as e:
        logger.error(f"Error in CategoryDeleteView: {e}")
        messages.error(request, 'An error occurred while processing the category.')
        return render(request, '404.html', {"message": "An error occurred."})

def ProductListView(request):
    try:
        product =Product.objects.all()
        paginator =Paginator(product,10)
        page_number =request.GET.get('page')
        page_obj =paginator.get_page(page_number)
        
        context ={
            "product":page_obj,
        }
        return render(request, 'product.html',context)

    except Exception as e:
        logger.error(f"Error in ProductListView: {e}")
        messages.error(request,"An error occurred while loading the product list.")
        return render(request, '404.html', {"message": "An error occurred."})

def ProductCreateView(request, product_id=None):
    try:
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            form = ProductForm(request.POST or None, request.FILES or None, instance=product)
            action = 'Update'
        else:
            form = ProductForm(request.POST or None, request.FILES or None)
            action = 'Create'

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, f'Product {action.lower()}d successfully!')
                return redirect('product')  # Update this with your product list view URL name
            else:
                messages.error(request, 'Please correct the errors below.')

        return render(request, 'product_create.html', {'form': form, 'action': action})
    except Exception as e:
        messages.error(request, 'An error occurred while processing the product.')
        logger.error(f"Error in ProductCreateView: {e}")
        return render(request, '404.html', {"message": "An error occurred."})

def ProductUpdateView(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)

        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('product')  # Update this with your product list view URL name
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProductForm(instance=product)

        return render(request, 'product_update.html', {'form': form, 'product': product})
    except Exception as e:
        logger.error(f"Error in ProductUpdateView: {e}")
        messages.error(request, 'An error occurred while updating the product.')
        return render(request, '404.html', {"message": "An error occurred."})

def ProductDeleteView(request,pk):
    try:
        product = get_object_or_404(Product,pk=pk)
        if request.method == 'POST':
            product_name = product.name
            product.delete()
            messages.success(request,f'Product {product_name} deleted successfully!')
            return redirect('product')
        return render(request, 'product_delete.html',{'product':product})
    except Exception as e:
        logger.error(f"Error in ProductDeleteView: {e}")
        messages.error(request, 'An error occurred while processing the product.')
        return render(request, '404.html', {"message": "An error occurred."})

def SalesListView(request):
    try:
        sales = Sales.objects.all()
        paginator = Paginator(sales, 10)  # Show 10 sales per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context={
            "sales":page_obj,
        }
        return render(request, 'sales.html',context)
    except Exception as e:
        logger.error(f"Error in SalesListView: {e}")
        return render(request, '404.html', {"message": "An error occurred."})

def SalesCreateView(request,sales_id=None):
    try:
        if sales_id:
            sales = get_object_or_404(Sales,id = sales_id)
            form = SalesForm(request.POST or None,instance=sales)
            action = 'Update'
        else:
            form = SalesForm(request.POST or None)
            action ='Create'
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, f" Sales {action.lower()}d successfully!")
                return redirect('sales')
        return render(request, 'sales_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in SalesCreateView: {e}")
        messages.error(request, 'An error occurred while processing the sales.')
        return render(request, '404.html', {"message": "An error occurred."})

def SalesUpdateView(request,pk):
    try:
        sales=get_object_or_404(Sales,pk=pk)
        if request.method == 'post':
            form=SalesForm(request.POST or None,instance=sales)
            if form.is_valid():
                form.save()
                messages.success(request,f'Sales updated successfully!')
                return redirect('sales')
        else:
            form=SalesForm(instance=sales)
        return render(request, 'sales_update.html',{'form':form,'sales':sales})
    except Exception as e:
        logger.error(f"Error in SalesUpdateView: {e}")
        messages.error(request, 'An error occurred while processing the sales.')
        return render(request, '404.html', {"message": "An error occurred."})

def SalesDeleteView(request,pk):
    try:
        sales =get_object_or_404(Sales,pk=pk)
        if request.method == 'POST':
            sales_name = sales.name
            sales.delete()
            messages.success(request,f'Sales {sales_name} deleted successfully!')
            return redirect('sales')
        return render(request, 'sale_delete.html',{'sales':sales})
    except Exception as e:
        logger.error(f"Error in SalesDeleteView: {e}")
        messages.error(request, 'An error occurred while processing the sales.')
        return render(request, '404.html', {"message": "An error occurred."})

def VendorListView(request):
    try:
        vendor=Vendor.objects.all().order_by('-id')
        paginator=Paginator(vendor,10)
        page_number=request.GET.get('page')
        page_obj=paginator.get_page(page_number)
        context={
            "vendors":page_obj,
        }
        return render(request, 'vendor.html',context)
    except Exception as e:
        logger.error(f"Error in VendorListView: {e}")
        return render(request, '404.html', {"message": "An error occurred."})

def VendorCreateView(request,vendor_id=None):
    try:
        if vendor_id:
            vendor = get_object_or_404(vendor,id =vendor_id)
            form =VendorForm(request.post or None,instance=vendor)
            action = 'update'
        else:
            form = VendorForm(request.post or None)
            action = 'create'
        if request.method == 'post':
            if form.is_valid():
                form.save()
                messages.success(request,f'Vendor {action.lower()}d successfully!')
                return redirect('vendor')
        return render(request, 'vendor_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in VendorCreateView: {e}")
        messages.error(request,"An error occurred while processing the vendor.")
        return redirect('404.html', {"message": "An error occurred."})
    
def VendorUpdateView(request,pk):
    try:
        vendor=get_object_or_404(Vendor,pk=pk)
        if request.method == 'post':
            form=VendorForm(Vendor,instance=vendor)
            if form.is_valid():
                form.save()
                messages.success(request,f'Vendor updated successfully!')
                return redirect('vendor')
        else:
            form =VendorForm(instance=vendor)
            return render(request, 'vendor_update.html',{'form':form,'vendor':vendor})
    except Exception as e:
        logger.error(f"Error in VendorUpdateView: {e}")
        messages.error(request,"An error occurred while processing the vendor.")
        return redirect('404.html', {"message": "An error occurred."})
    
def VendorDeleteView(request,pk):
    try:
        vendor=get_object_or_404(Vendor,pk=pk)
        if request.method == 'POST':
            vendo_name = vendor.name
            vendor.delete()
            messages.success(request,f'Vendor {vendo_name} deleted successfully!')
            return redirect('vendor')
        return render(request, 'vendor_delete.html',{'vendor':vendor})
    except Exception as e:
        logger.error(f"Error in VendorDeleteView: {e}")
        messages.error(request,"An error occurred while processing the vendor.")
        return redirect('404.html', {"message": "An error occurred."})

def PurchaseListView(request):
    try:
        purches=Purchase.objects.all()
        pagination =Paginator(purches,10)
        page_number=request.GET.get('page')
        page_obj=pagination.get_page(page_number)
        context={
            'purches':page_obj,
        }
        return render(request, 'purchases.html',context)
    except Exception as e:
        logger.error(f"Error in PurchaseListView: {e}")
        messages.error(request, 'An error occurred while loading the purchase list.')
        return render(request, '404.html', {"message": "An error occurred."})

def PurchaseCreateView(request,pruchase_id=None):
    try:
        if pruchase_id:
            purchase=get_object_or_404(Purchase,id=pruchase_id)
            form=PurchaseForm(request.POST or None,instance=purchase)
            action='update'
        else:
            form=PurchaseForm(request.POST or None)
            action='create'
        if request.method == 'post':
            if form.is_valid():
                form.save()
                messages.success(request,f'Purchase {action.lower()}d successfully!')
                return redirect('purchases')
        return render(request, 'purchases_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in PurchaseCreateView: {e}")
        messages.error(request, 'An error occurred while processing the purchase.')
        return render(request, '404.html', {"message": "An error occurred."})

def PurchaseUpdateView(request,pk):
    try:
        purchase = get_object_or_404(Purchase,pk=pk)
        if request.method == 'POST':
            form= PurchaseForm(request.POST,instance=purchase)
            if form.is_valid():
                form.save()
                messages.success(request,f'Purchase updated successfully!')
                return redirect('purchases')
        else:
            form = PurchaseForm(instance=purchase)
            return render(request, 'purchases_update.html',{'form':form,'purchase':purchase})
    except Exception as e:
        logger.error(request, 'An error occurred while processing the purchase.')
        messages.error(request, 'An error occurred while processing the purchase.')
        return render(request, '404.html', {"message": "An error occurred."})

def PurchaseDeleteView(request,pk):
    try:
        purchase= get_object_or_404(Purchase,pk=pk)
        if request.method == 'POST':
            purchase_name=purchase.nam
            purchase.delete()
            messages.success(request,f'Purchase {purchase_name} deleted successfully!')
            return redirect('purchases')
        return render(request, 'purchase_delete.html',{'purchase':purchase})
    except Exception as e:
        logger.error(f"Error in PurchaseDeleteView: {e}")
        messages.error(request, 'An error occurred while processing the purchase.')
        return render(request, '404.html', {"message": "An error occurred."})

def RepairListView(request):
    try:
        repair=Repair.objects.all()
        pagination=Paginator(repair,10)
        page_number=request.GET.get('page')
        page_obj=pagination.get_page(page_number)
        context={
            'repair':page_obj,
        }
        return render(request, 'repair.html',context)
    except Exception as e:
        logger.error(f'An error occurred while loading the repair list:- {e}')
        messages.error(request, 'An error occurred while loading the repair list.')
        return render(request, '404.html', {"message": "An error occurred."})
    
def RepairCreateView(request,repair_id=None):
    try:
        if repair_id:
            repair=get_object_or_404(Repair,id=repair_id)
            form=RepairForm(request.POST or None,instance=repair)
            action='update'
        else:
            form=RepairForm(request.POST or None)
            action='create'
        if request.method == 'post':
            if form.is_valid():
                form.save()
                messages.success(request,f'Repair {action.lower()}d successfully!')
                return redirect('repair')
        return render(request, 'repair_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in RepairCreateView: {e}")
        messages.error(request, 'An error occurred while processing the repair.')
        return render(request, '404.html', {"message": "An error occurred."})
    
def RepairUpdateView(request,pk):
    try:
        repair=get_object_or_404(Repair,pk=pk)
        if request.method =='post':
            form=RepairForm(request.POST or None,instance=repair)
            if form.is_valid():
                form.save()
                messages.success(request,f'Repair updated successfully!')
                return redirect('repair')
        else:
            form=RepairForm(instance=repair)
            return render(request, 'repair_update.html',{'form':form,'repair':repair})
    except Exception as e:
        logger.error(f"Error in RepairUpdateView: {e}")
        messages.error(request, 'An error occurred while processing the repair.')
        return render(request, '404.html', {"message": "An error occurred."})

def RepairDeleteView(request,pk):
    try:
        repair=get_object_or_404(RepairDetail,pk=pk)
        if request.method == 'post':
            repair_name=repair.name
            repair.delete()
            messages.success(request,f'Repair {repair_name} deleted successfully!')
            return redirect('repair')
        return render(request, 'repair_delete.html',{'repair':repair})
    except Exception as e:
        logger.error(f"Error in RepairDeleteView{pk}: {e}")
        messages.error(request, 'An error occurred while processing the repair.')
        return render(request, '404.html', {"message": "An error occurred."})

def RepairDetailListView(request):
    try:
        repairdetail = RepairDetail.objects.all()
        pagination = Paginator(repairdetail, 10)
        page_number = request.GET.get('page') 
        page_obj = pagination.get_page(page_number)
        context = {
            'repairdetail': page_obj,
        }
        return render(request, 'repairdetail.html', context)
    except Exception as e:
        logger.error(f"Error in RepairListView: {e}")
        messages.error(request, 'An error occurred while loading the repair detail list.')
        return render(request, '404.html', {"message": "An error occurred."})
    
def RepairDetailCreate(request,repairde_id=None):
    try:
        if repairde_id:
            repairdetail=get_object_or_404(RepairDetail,id=repairde_id)
            form=RepairDetail(request.POST or None,instance=repairdetail)
            action='Update'
        else:
            form = RepairDetailForm(request.POST or None)
            action = 'Create'
            if request.method == 'Post':
                if form.is_valid():
                    form.save()
                    messages.success(request,f'Repair Detail {action.lower()}d successfully!')
                    return redirect('repairdetail')
            return render(request, 'repair_detail_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in RepairDetailCreateView: {e}")
        messages.error(request, 'An error occurred while processing the repair detail.')
        return render(request, '404.html', {"message": "An error occurred."})

def RepairDetailUpdateView(request,pk):
    try:
        repairdetail=get_object_or_404(RepairDetail,pk=pk)
        if request.method == 'POST':
            form=RepairDetailForm(request.POST or None,instance=repairdetail)
            if form.is_valid():
                form.save()
                messages.success(request,f'Repair Detail updated successfully!')
                return redirect('repairdetail')
        else:
            form =RepairDetailForm(instance=repairdetail)
            return render(request, 'repair_detail_update.html', {'form': form, 'repairdetail': repairdetail})
    except Exception as e:
        logger.error(f"Error in RepairDetailUpdateView: {e}")
        messages.error(request, 'An error occurred while processing the repair detail.')
        return render(request, '404.html', {"message": "An error occurred."})
    
def RepairDetailDeleteView(request,pk):
    try:
        repairdetail=get_object_or_404(RepairDetail,pk=pk)
        if request.method == 'post':
            repairdetail_name=repairdetail.name
            repairdetail.delete()
            messages.success(request,f'Repair Detail {repairdetail_name} deleted successfully!')
            return redirect('repairdetail')
        return render(request, 'repair_detail_delete.html',{'repairdetail':repairdetail})
    except Exception as e:
        logger.error(f"Error in RepairDetailDeleteView: {e}")
        messages.error(request, 'An error occurred while processing the repair detail.')
        return render(request, '404.html', {"message": "An error occurred."})

def InvoiceListView(request):
    try:
        invoice=Invoice.objects.all()
        pagination=Paginator(invoice,10)
        page_number=request.GET.get('page')
        page_obj=pagination.get_page(page_number)
        context={
            "invoice":page_obj,
        }
        return render(request, 'invoice.html',context)
    except Exception as e:
        logger.error(f"Error in occurred while loading the invoice list.': {e}") 
        messages.error(request, 'An error occurred while loading the invoice list.')
        return render(request, '404.html', {"message": "An error occurred."})

def InvoiceCreateView(request,invoice_id=None):
    try:
        if invoice_id:
            invoice=get_object_or_404(Invoice,id=invoice_id)
            form=InvoiceForm(request.POST or None,instance=invoice)
            action='update'
        else:
            form=InvoiceForm(request.POST or None)
            action='create'
        if request.method == 'post':
            if form.is_valid():
                form.save()
                messages.success(request, f'Invoice {action.lower()}d successfully!')
                return redirect('invoice')
        return render(request, 'invoice_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in InvoiceCreateView: {e}")
        messages.error(request, 'An error occurred while processing the invoice.')
        return render(request, '404.html', {"message": "An error occurred."})

def InvoiceUpdateView(request,pk):
    try:
        invoice=get_object_or_404(Invoice, pk=pk)
        if request.method == 'POST':
            form=InvoiceForm(request.POST or None, instance=invoice)
            if form.is_valid():
                form.save()
                messages.success(request, f'Invoice updated successfully!')
                return redirect('invoice')
        else:
            form = InvoiceForm(instance=invoice)
            return render(request, 'invoice_update.html',{'form':form,'invoice':invoice})
    except Exception as e:
        logger.error(f"Error in InvoiceUpdateView: {e}")
        messages.error(request, 'An error occurred while processing the invoice.')
        return render(request, '404.html', {"message": "An error occurred."})

def Invoiceprint(request):
    return render(request, 'invoice_print.html',)

def ReportListView(request):
    try:
        report=Report.objects.all()
        pagination=Paginator(report, 10)
        page_number=request.GET.get('page')
        page_obj=pagination.get_page(page_number)
        context={
            'report':page_obj,
        }
        return render(request, 'report.html',context)
    except Exception as e:
        logger.error(f"Error in ReportListView: {e}")
        messages.error(request, 'An error occurred while loading the report list.')
        return render(request, '404.html', {"message": "An error occurred."})

