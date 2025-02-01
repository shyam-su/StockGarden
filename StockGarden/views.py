from django.shortcuts import render
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
import logging
from django.core.paginator import Paginator
from django.contrib import messages  
import pickle as pk
from django.db.models import Avg, Sum, Min, Max, Count
from django.db.models import Q





# Create your views here
# Set up logging
logger = logging.getLogger(__name__)
def home(request):
    try:
        total = Sales.objects.aggregate(Sum('total'))
        total_products = Product.objects.count()
        pending_repairs = Repair.objects.filter(status='in-progress').count()
        context={
            'total':total,
            'total_product':total_products,
            'pending_repairs':pending_repairs
        }
        return render(request, 'home.html', context)
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        messages.error(request, 'An error occurred while loading the brand list.')
    return render(request, '404.html', {"message": "An error occurred while loading the brand list."})


def BrandListView(request):
    try:
        query = request.GET.get('q', '')
        # Fetch all brands and order them by ID (descending)
        brands = Brand.objects.all().order_by('-id')
        
        if query:
            brands = brands.filter(name__icontains=query)

        # Paginate the brands, showing 10 per page
        paginator = Paginator(brands, 10)
        page_number = request.GET.get('page')  # Get the current page number from the request
        page_obj = paginator.get_page(page_number)  # Get the page object

        # Context to be passed to the template
        context = {
            "brand": page_obj,
            "query": query,
            }
        return render(request, 'brand.html', context)  # Render the template with context
    except Exception as e:
        # Log the exception for debugging
        logger.error(f"Error in BrandListView: {e}")
        
        # Add an error message to display to the user
        messages.error(request, 'An error occurred while loading the brand list.')
        
        # Optionally, render an error page or redirect to a fallback page
        return render(request, '404.html', {"message": "An error occurred while loading the brand list."})


def BrandCreateView(request, brand_id=None):
    try:
        if brand_id:  # Check if we are updating an existing brand
            brand = get_object_or_404(Brand, id=brand_id)
            form = BrandForm(request.POST or None, request.FILES or None, instance=brand)
            action = "Update"
        else:  # Creating a new brand
            form = BrandForm(request.POST or None, request.FILES or None)
            action = "Create"

        if request.method == 'POST':
            if form.is_valid():
                form.save()  # Save the brand to the database
                messages.success(request, f'Brand {action.lower()}d successfully!')
                return redirect('brand')  # Redirect to the brand list view after successful creation/update

        return render(request, 'brand_create.html', {'form': form, 'action': action})
    
    except Exception as e:
        # Log or handle any unexpected errors
        messages.error(request, 'An error occurred. Please try again later.')
        return redirect('brand')

    except Exception as e:
        logger.error(f"Error in BrandCreateView: {e}")
        messages.error(request, 'An error occurred while processing the brand.')
        return render(request, '404.html', {"message": "An error occurred."})

def BrandUpdateView(request, pk):
    try:
        brand = get_object_or_404(Brand, pk=pk)

        if request.method == 'POST':
            form = BrandForm(request.POST or None, request.FILES or None, instance=brand)
            if form.is_valid():
                form.save()
                # Add a success message after updating
                messages.success(request, f"The brand '{brand.name}' has been successfully updated.")
                return redirect('brand')  # Redirect back to the brand list page after saving
        else:
            form = BrandForm(request.POST or None, request.FILES or None, instance=brand)

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
        query = request.GET.get('q', '').strip()
        category =Category.objects.all().order_by('-id')

        if query:
            logger.info(f"Searching for category: {query}")  # Debugging log
            category = category.filter(
                Q(name__icontains=query)  # Search by category name
            )


        paginator =Paginator(category,10)
        page_number =request.GET.get('page')
        page_obj = paginator.get_page(page_number)        
        context={
            "category":page_obj,
            "query": query,  # Pass search query to template
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
        query = request.GET.get('q', '')
        product =Product.objects.all().order_by('-id')

        if query:
            product = product.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(categories__name__icontains=query)
            )

        paginator =Paginator(product,10)
        page_number =request.GET.get('page')
        page_obj =paginator.get_page(page_number)
        
        context ={
            "product":page_obj,
            "query": query,
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
        query = request.GET.get('q', '')
        sales = Sales.objects.all().order_by('-id')

        if query:
            sales = sales.filter(
                Q(name__full_name__icontains=query) |  # Search by user (seller name)
                Q(product__name__icontains=query) |  # Search by product name
                Q(contact_no__icontains=query)  # Search by contact number
            )

        paginator = Paginator(sales, 10)  # Show 10 sales per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context={
            "sales":page_obj,
            "query": query,
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

def SalesUpdateView(request, pk):
    try:
        sales = get_object_or_404(Sales, pk=pk)

        if request.method == 'POST':  # Fixing method check
            form = SalesForm(request.POST, instance=sales)  # Changed to request.POST
            if form.is_valid():
                form.save()
                messages.success(request, f'Sales updated successfully!')
                return redirect('sales')  # Ensure 'sales' is a valid URL name
        else:
            form = SalesForm(instance=sales)  # Initialize form without POST data

        return render(request, 'sales_update.html', {'form': form, 'sales': sales})
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
        return render(request, 'sales_delete.html',{'sales':sales})
    except Exception as e:
        logger.error(f"Error in SalesDeleteView: {e}")
        messages.error(request, 'An error occurred while processing the sales.')
        return render(request, '404.html', {"message": "An error occurred."})

def VendorListView(request):
    try:
        query = request.GET.get('q', '')
        vendor=Vendor.objects.all().order_by('-id')

        if query:
            vendor = vendor.filter(
                Q(name__full_name__icontains=query) |  # Search by  name
                Q(company_name__icontains=query) |      # Search by company name
                Q(contact_no__icontains=query) |         # Search by contact number
                Q(email__icontains=query) |
                Q(address__icontains=query)
            )


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
            vendor = get_object_or_404(Vendor,id=vendor_id)
            form =VendorForm(request.POST or None,instance=vendor)
            action = 'update'
        else:
            form = VendorForm(request.POST or None)
            action = 'create'
        if request.method == 'POST':
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
        if request.method == 'POST':
            form=VendorForm(request.POST or None,instance=vendor)
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
        query = request.GET.get('q', '')
        purches=Purchase.objects.all()

        if query:
            purches = purches.filter(
                Q(vendor__company_name__icontains=query) |  # Search by Vendor's company name
                Q(product__name__icontains=query) |        # Search by Product name
                Q(description__icontains=query)            # Search by Description
            )


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
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request,f'Purchase {action.lower()}d successfully!')
                return redirect('purchase')
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
                return redirect('purchase')
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
            purchase_name=purchase.product.name
            purchase.delete()
            messages.success(request,f'Purchase {purchase_name} deleted successfully!')
            return redirect('purchase')
        return render(request, 'purchase_delete.html',{'purchase':purchase})
    except Exception as e:
        logger.error(f"Error in PurchaseDeleteView: {e}")
        messages.error(request, 'An error occurred while processing the purchase.')
        # return render(request, '404.html', {"message": "An error occurred."})

def RepairListView(request):
    try:
        query = request.GET.get('q', '')
        repair=Repair.objects.all().order_by('id')

        if query:
            repair = repair.filter(
                Q(product_name__icontains=query) | 
                Q(device_model__icontains=query) |
                Q(name__full_name__icontains=query)  # Search by customer username
            )

        pagination=Paginator(repair,10)
        page_number=request.GET.get('page')
        page_obj=pagination.get_page(page_number)
        context={
            'repair':page_obj,
            'query': query,
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
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request,f'Repair {action.lower()}d successfully!')
                return redirect('repair')
            else:
                print("Form Errors:", form.errors)  # For debugging
                messages.error(request, 'Form is invalid.')
        return render(request, 'repair_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in RepairCreateView: {e}")
        messages.error(request, 'An error occurred while processing the repair.')
        return render(request, '404.html', {"message": "An error occurred."})
    
def RepairUpdateView(request,pk):
    try:
        repair=get_object_or_404(Repair,pk=pk)
        if request.method =='POST':
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
        repair=get_object_or_404(Repair,pk=pk)
        if request.method == 'POST':
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
        query = request.GET.get('q', '')
        repairdetail = RepairDetail.objects.all().order_by('id')

        if query:
            repairdetail = repairdetail.filter(
                Q(repair_order__product_name__icontains=query) |  # You can search by repair_order product_name
                Q(fixed_description__icontains=query) |  # Search by fixed_description
                Q(repair_action__icontains=query)  # Search by repair_action
            )
        pagination = Paginator(repairdetail, 10)
        page_number = request.GET.get('page') 
        page_obj = pagination.get_page(page_number)
        context = {
            'repairdetail': page_obj,
            'query': query,
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
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    messages.success(request,f'Repair Detail {action.lower()}d successfully!')
                    return redirect('repair_detail')
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
                return redirect('repair_detail')
        else:
            form =RepairDetailForm(instance=repairdetail)
            return render(request, 'repair_detail_update.html', {'form': form, 'repairdetail': repairdetail})
    except Exception as e:
        logger.error(f"Error in RepairDetailUpdateView: {e}")
        messages.error(request, 'An error occurred while processing the repair detail.')
        return render(request, '404.html', {"message": "An error occurred."})
    
def RepairDetailDeleteView(request, pk):
    try:
        # Retrieve the repair detail object or raise 404
        repairdetail = get_object_or_404(RepairDetail, pk=pk)

        if request.method == 'POST':
            # Safely access the product name
            repairdetail_name = repairdetail.repair_order.product_name
            repairdetail.delete()

            # Success message and redirect
            messages.success(request, f"Repair Detail '{repairdetail_name}' deleted successfully!")
            return redirect('repair_detail')  # Ensure this URL name is correct

        # Render the confirmation template
        return render(request, 'repair_detail_delete.html', {'repairdetail': repairdetail, 'deleted': False})

    except Exception as e:
        # Log the error and display an error message
        logger.error(f"Error in RepairDetailDeleteView: {e}", exc_info=True)
        messages.error(request, 'An error occurred while processing the repair detail. Please try again later.')
        return render(request, '404.html', {"message": "An error occurred."})

def InvoiceListView(request):
    try:
        invoice=Invoice.objects.all().order_by('id')
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
        if request.method == 'POST':
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

def UserReportListView(request):
    try:
        user=User.objects.all()
        pagination=Paginator(user, 10)
        page_number=request.GET.get('page')
        page_obj=pagination.get_page(page_number)
        context={
            'report':page_obj,
        }
        return render(request, 'user_report.html',context)
    except Exception as e:
        logger.error(f"Error in ReportListView: {e}")
        messages.error(request, 'An error occurred while loading the report list.')
        return render(request, '404.html', {"message": "An error occurred."})
    



def global_search(request):
    query = request.GET.get('q')
    if query:
        # Search in multiple models
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        sales = Sales.objects.filter(Q(name__full_name__icontains=query) | Q(product__name__icontains=query))
        purchases = Purchase.objects.filter(Q(vendor__company_name__icontains=query) | Q(product__name__icontains=query))
        repairs = Repair.objects.filter(Q(product_name__icontains=query) | Q(device_model__icontains=query) | Q(name__full_name__icontains=query))
        vendors = Vendor.objects.filter(Q(company_name__icontains=query) | Q(name__full_name__icontains=query))
        brands = Brand.objects.filter(Q(name__icontains=query))
        categories = Category.objects.filter(Q(name__icontains=query))
        users = User.objects.filter(Q(full_name__icontains=query))

        context = {
            'products': products,
            'sales': sales,
            'purchases': purchases,
            'repairs': repairs,
            'vendors': vendors,
            'brands': brands,
            'categories': categories,
            'users': users,
            'query': query,
        }
    else:
        context = {}

    return render(request, 'search_results.html', context)


from django.db.models import F

def SalesReportListView(request):
    sales = Sales.objects.annotate(total_amount=F('quantity') * F('price'))

    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        sales = sales.filter(created_at__date__range=[start_date, end_date])

    # Calculate totals
    total_quantity = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = { 
        'sales': sales,
        'total_quantity': total_quantity,
    }
    return render(request, 'sales_report.html', context)

def RepairReportListView(request):
    return render(request, 'product_report.html')

def StockReportListView(request):
    return render(request, 'product_report.html')


def RepairReportListView(request):
    # Get filter parameters from request
    status = request.GET.get('status', '')  
    customer_id = request.GET.get('customer', '')  

    # Base queryset
    repairs = Repair.objects.all().order_by('-created_at')  

    # Apply filters
    if status:
        repairs = repairs.filter(status=status)
    if customer_id:
        repairs = repairs.filter(name_id=customer_id)  # ForeignKey lookup

    # Pagination (10 items per page)
    paginator = Paginator(repairs, 10)
    page_number = request.GET.get('page')
    repairs_page = paginator.get_page(page_number)

    # Pass all customers for filtering dropdown
    customers = User.objects.filter(role="Customer").order_by('full_name')

    context = {
        'repairs': repairs_page,
        'customers': customers,
        'selected_status': status,
        'selected_customer': customer_id,
    }
    return render(request, 'repair_report.html', context)


def RepairDetailReportListView(request):
    # Get filter parameters from request
    repair_order_id = request.GET.get('repair_order', '')  
    repair_action = request.GET.get('repair_action', '')  

    # Base queryset
    repair_details = RepairDetail.objects.select_related('repair_order').order_by('-created_at')

    # Apply filters
    if repair_order_id:
        repair_details = repair_details.filter(repair_order_id=repair_order_id)
    if repair_action:
        repair_details = repair_details.filter(repair_action=repair_action)

    # Pagination (10 items per page)
    paginator = Paginator(repair_details, 10)
    page_number = request.GET.get('page')
    repair_details_page = paginator.get_page(page_number)

    # Pass all repair orders for filtering dropdown
    repair_orders = Repair.objects.all().order_by('-created_at')

    context = {
        'repair_details': repair_details_page,
        'repair_orders': repair_orders,
        'selected_repair_order': repair_order_id,
        'selected_repair_action': repair_action,
    }
    return render(request, 'repair_detail_report.html', context)



