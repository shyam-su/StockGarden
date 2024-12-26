from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
import logging
from django.core.paginator import Paginator
from django.contrib import messages  # Import messages




# Create your views here

# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html',)

# @cache_page(60 * 10)  # Cache the view for 10 minutes
def BrandListView(request):
    try:
        brands = Brand.objects.all()
        paginator = Paginator(brands, 10)  # Show 10 brands per page

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Add a message when the page loads successfully
        messages.success(request, 'Brand list loaded successfully.')

        context = {"brand": page_obj}
        return render(request, 'brand.html', context)
    except Exception as e:
        logger.error(f"Error in BrandListView: {e}")
        # Add an error message if something goes wrong
        messages.error(request, 'An error occurred while loading the brand list.')

        return render(request, 'error.html', {"message": "An error occurred."})


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
        return render(request, 'error.html', {"message": "An error occurred."})

# @cache_page(60 * 10)  # Cache the view for 10 minutes
def BrandUpdateView(request, pk):
    try:
        brand = get_object_or_404(Brand, pk=pk)

        if request.method == 'POST':
            form = BrandForm(request.POST, instance=brand)
            if form.is_valid():
                form.save()
                # Add a success message after updating
                messages.success(request, f"The brand '{brand.name}' has been successfully updated.")
                # Clear the cache for the brand list page after updating to ensure the list is updated
                cache.delete('brand_list')  # You can change the cache key if needed
                return redirect('brand')  # Redirect back to the brand list page after saving
        else:
            form = BrandForm(instance=brand)

        return render(request, 'brand_update.html', {'form': form, 'brand': brand})

    except Exception as e:
        logger.error(f"Error in BrandUpdateView for brand {pk}: {e}")
        messages.error(request, 'An error occurred while updating the brand.')
        return render(request, 'error.html', {"message": "An error occurred while updating the brand."})

# @cache_page(60 * 10)  # Cache the view for 10 minute

def BrandDeleteView(request, pk):
    try:
        # Get the brand object or raise a 404 error if not found
        brand = get_object_or_404(Brand, pk=pk)

        if request.method == 'POST':
            brand_name = brand.name  # Store the brand name before deletion
            brand.delete()  # Delete the brand

            # Add a success message after deletion
            messages.success(request, f"The brand '{brand_name}' has been successfully deleted.")
            
            # Clear the cache for the brand list page to ensure it's updated
            cache.delete('brand')  # Adjust cache key if necessary

            # Redirect to the brand list or another appropriate page
            return redirect('brand')  # Assuming 'brand_list' is the name of the URL pattern for the brand list page

        # If it's not a POST request, render the confirmation page for deletion
        return render(request, 'brand_delete.html', {'brand': brand})

    except Exception as e:
        # Log the error and display a friendly error message
        logger.error(f"Error in BrandDeleteView for brand {pk}: {e}")
        messages.error(request, 'An error occurred while deleting the brand.')
        
        # Redirect to a safe page instead of rendering a 404 error page
        return redirect('brand')  # Redirect to the brand list page or an appropriate page for error handling


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
    return render(request, '404.html',)

def ReportCreateView(request):
    return render(request, 'home.html',)

def ReportUpdateView(request):
    return render(request, 'home.html',)

def ReportDeleteView(request):
    return render(request, 'home.html',)
