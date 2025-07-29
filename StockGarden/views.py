import logging
import json
import openpyxl
from django.shortcuts import HttpResponse,render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.contrib import messages  
from django.db.models import Sum,Q,Count
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from django.utils import timezone
from user.permissions import role_required, admin_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import csv




# Create your views here
logger = logging.getLogger(__name__)

@login_required
def home(request):
    try:
        time_period = request.GET.get('period', 'week')

        # Card Data Calculations (Overall totals)
        total_sales = Sales.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_repair = RepairDetail.objects.aggregate(total=Sum('repair_cost'))['total'] or 0
        total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_earning = (total_sales + total_repair) - total_expenses
        low_stock_count = Product.objects.filter(stock__lt=5).count()
        
        # Metrics for cards
        metrics = {
            'total_earning': total_earning,
            'total_products': Product.objects.count(),
            'total_categories': Category.objects.count(),
            'total_brands': Brand.objects.count(),
            'pending_repairs': Repair.objects.filter(status='in-progress').count(),
            'low_stock': low_stock_count,
            'completed_repairs': Repair.objects.filter(status='completed').count(),
            'product_categories': Category.objects.count(),
            'product_brands': Brand.objects.count(),
        }
        
        # Chart Data - Filter by selected period
        months = []
        earnings_data = []
        expenses_data = []
        sales_data = []
        repair_data = []
        
        end_date = timezone.now()
        
        if time_period == 'week':
            start_date = end_date - timedelta(days=7)
            date_format = '%d %b'
            delta = timedelta(days=1)
        elif time_period == 'month':
            start_date = end_date - timedelta(days=30)
            date_format = '%d %b'
            delta = timedelta(days=1)
        elif time_period == '3months':
            start_date = end_date - timedelta(days=90)
            date_format = '%b %d'
            delta = timedelta(days=7)
        else:  # 6months
            start_date = end_date - timedelta(days=180)
            date_format = '%b %Y'
            delta = timedelta(days=30)
        
        current_date = start_date
        while current_date <= end_date:
            if time_period in ['week', 'month']:
                date_label = current_date.strftime(date_format)
                next_date = current_date + timedelta(days=1)
            elif time_period == '3months':
                date_label = f"Week {current_date.isocalendar()[1]}"
                next_date = current_date + timedelta(weeks=1)
            else:  # 6months
                date_label = current_date.strftime('%b')
                next_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            
            sales = Sales.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            repairs = RepairDetail.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).aggregate(total=Sum('repair_cost'))['total'] or 0
            
            expenses = Expense.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            earnings = (sales + repairs) - expenses
            
            months.append(date_label)
            earnings_data.append(earnings)
            expenses_data.append(expenses)
            sales_data.append(sales)
            repair_data.append(repairs)
            
            current_date = next_date
        
        period_total_sales = sum(sales_data)
        period_total_repair = sum(repair_data)
        
        context = {
            **metrics,
            'months': months,
            'sales_data': sales_data,
            'repair_data': repair_data,
            'total_sales': total_sales,  
            'total_repair': total_repair, 
            'total_expenses': total_expenses,  
            'period_total_sales': period_total_sales,  
            'period_total_repair': period_total_repair, 
            'sales_percentage': (period_total_sales / (period_total_sales + period_total_repair) * 100) if (period_total_sales + period_total_repair) > 0 else 0,
            'repair_percentage': (period_total_repair / (period_total_sales + period_total_repair) * 100) if (period_total_sales + period_total_repair) > 0 else 0,
            'selected_period': time_period,
            'earnings_data': earnings_data,
            'expenses_data': expenses_data,
        }
        return render(request, 'home.html', context)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render(request, '404.html', {'message': 'Failed to load dashboard data'})
    

@login_required
def BrandList(request):
    try:
        query = request.GET.get('query', '')
        brands = Brand.objects.all().order_by('-id')
        if query:
            brands = brands.filter(name__icontains=query)
            
        for brand in brands:
            if not brand.image:
                brand.image_url = None
            else:
                brand.image_url = brand.image.url
                
        paginator = Paginator(brands, 10)
        page_number = request.GET.get('page') 
        page_obj = paginator.get_page(page_number)

        context = {
            "brand": page_obj,
            "query": query,
            }
        return render(request, 'brand.html', context) 
    except Exception as e:
        logger.error(f"Error in BrandListView: {e}")
        messages.error(request, 'An error occurred while loading the brand list.')
        return render(request, '404.html', {"message": "An error occurred while loading the brand list."})

@role_required('admin',)
@login_required
def BrandCreate(request, brand_id=None):
    try:
        if brand_id:
            brand = get_object_or_404(Brand, id=brand_id)
            form = BrandForm(request.POST or None, request.FILES or None, instance=brand)
            action = "Update"
        else:
            form = BrandForm(request.POST or None, request.FILES or None)
            action = "Create"

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, f'Brand {action.lower()}d successfully!')
                return redirect('brand')

        return render(request, 'brand_create.html', {'form': form, 'action': action})
    
    except Exception as e:
        messages.error(request, 'An error occurred. Please try again later.')
        return redirect('brand')
    
    except Exception as e:
        logger.error(f"Error in BrandCreateView: {e}")
        messages.error(request, 'An error occurred while processing the brand.')
        return render(request, '404.html', {"message": "An error occurred."})

@role_required('admin',)
@login_required
def BrandUpdate(request, pk):
    try:
        brand = get_object_or_404(Brand, pk=pk)

        if request.method == 'POST':
            form = BrandForm(request.POST or None, request.FILES or None, instance=brand)
            if form.is_valid():
                form.save()
                messages.success(request, f"The brand '{brand.name}' has been successfully updated.")
                return redirect('brand')
        else:
            form = BrandForm(request.POST or None, request.FILES or None, instance=brand)
        return render(request, 'brand_update.html', {'form': form, 'brand': brand})

    except Exception as e:
        logger.error(f"Error in BrandUpdateView for brand {pk}: {e}")
        messages.error(request, 'An error occurred while updating the brand.')
        return render(request, 'error.html', {"message": "An error occurred while updating the brand."})

@role_required('admin',)
@login_required
def BrandDelete(request, pk):
    try:
        brand = get_object_or_404(Brand, pk=pk)

        if request.method == 'POST':
            brand_name = brand.name  
            brand.delete()  
            messages.success(request, f"The brand '{brand_name}' has been successfully deleted.")
            return redirect('brand')  

        return render(request, 'brand_delete.html', {'brand': brand})
    except Exception as e:
        logger.error(f"Error in BrandDeleteView for brand {pk}: {e}")
        messages.error(request, 'An error occurred while deleting the brand.')
        return render(request, '404.html', {"message": "An error occurred while deleting the brand."})

@login_required
def CategoryList(request):
    try:
        query = request.GET.get('query', '').strip()
        category =Category.objects.all().order_by('-id')

        if query:
            logger.info(f"Searching for category: {query}")
            category = category.filter(
                Q(name__icontains=query) 
            )


        paginator =Paginator(category,10)
        page_number =request.GET.get('page')
        page_obj = paginator.get_page(page_number)        
        context={
            "category":page_obj,
            "query": query, 
        }
        return render(request,'category.html',context)
    except Exception as e:
        logger.error(f" Error in CategoryListView: {e}")
        return render(request, '404.html', {"message": "An error occurred."})
    
@login_required
def CategoryCreate(request,catagory_id=None):
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
    
@login_required    
def CategoryUpdate(request,pk):
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

@login_required
def CategoryDelete(request,pk):
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

@login_required
def purchase_items_list(request, voucher_pk):
    """List all items for a specific voucher"""
    voucher = get_object_or_404(PurchaseVoucher, pk=voucher_pk)
    items = voucher.items.select_related('brand', 'category').all()
    
    context = {
        'voucher': voucher,
        'items': items,
        'title': f'Items for Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'purchases/purchase_items_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def purchase_item_create(request, voucher_pk):
    """Add a new item to an existing voucher"""
    voucher = get_object_or_404(PurchaseVoucher, pk=voucher_pk)
    
    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = form.save(commit=False)
                    item.voucher = voucher
                    item.save()
                    
                    # Update voucher totals
                    voucher.update_totals()
                    
                    messages.success(request, 'Item added successfully!')
                    return redirect('purchase_items_list', voucher_pk=voucher.pk)
                    
            except Exception as e:
                messages.error(request, f'Error adding item: {str(e)}')
    else:
        form = PurchaseItemForm()
    
    context = {
        'form': form,
        'voucher': voucher,
        'title': f'Add Item to Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'purchases/purchase_item_create.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def purchase_item_update(request, voucher_pk, pk):
    """Update an existing purchase item"""
    voucher = get_object_or_404(PurchaseVoucher, pk=voucher_pk)
    item = get_object_or_404(PurchaseItem, pk=pk, voucher=voucher)
    
    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, request.FILES, instance=item)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    
                    # Update voucher totals
                    voucher.update_totals()
                    
                    messages.success(request, 'Item updated successfully!')
                    return redirect('purchase_items_list', voucher_pk=voucher.pk)
                    
            except Exception as e:
                messages.error(request, f'Error updating item: {str(e)}')
    else:
        form = PurchaseItemForm(instance=item)
    
    context = {
        'form': form,
        'voucher': voucher,
        'item': item,
        'title': f'Update Item in Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'purchases/purchase_item_update.html', context)


@login_required
@require_http_methods(["POST"])
def purchase_item_delete(request, voucher_pk, pk):
    """Delete a purchase item"""
    voucher = get_object_or_404(PurchaseVoucher, pk=voucher_pk)
    item = get_object_or_404(PurchaseItem, pk=pk, voucher=voucher)
    
    try:
        with transaction.atomic():
            item.delete()
            
            # Update voucher totals
            voucher.update_totals()
            
            messages.success(request, 'Item deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting item: {str(e)}')
    
    return redirect('purchase_items_list', voucher_pk=voucher.pk)

@login_required
def purchase_list(request):
    """List all purchase vouchers with search and filter functionality"""
    vouchers = PurchaseVoucher.objects.select_related('vendor').prefetch_related('items').all()
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        vouchers = vouchers.filter(
            Q(voucher_number__icontains=query) |
            Q(vendor__full_name__icontains=query) |
            Q(vendor__username__icontains=query) |
            Q(items__product_name__icontains=query)
        ).distinct()
    
    # Date filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Status filtering
    status = request.GET.get('status')
    if status:
        vouchers = vouchers.filter(status=status)
    
    # Pagination
    paginator = Paginator(vouchers, 25)  # 25 vouchers per page
    page_number = request.GET.get('page')
    vouchers = paginator.get_page(page_number)
    
    context = {
        'vouchers': vouchers,
        'query': query,
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
    }
    
    return render(request, 'purchases.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def purchase_create(request):
    """Create a new purchase voucher with items"""
    if request.method == 'POST':
        voucher_form = PurchaseVoucherForm(request.POST)
        item_form = PurchaseItemForm(request.POST, request.FILES)
        
        if voucher_form.is_valid() and item_form.is_valid():
            try:
                with transaction.atomic():
                    # Save voucher
                    voucher = voucher_form.save()
                    
                    # Save item and link to voucher
                    item = item_form.save(commit=False)
                    item.voucher = voucher
                    item.save()
                    
                    # Update voucher totals
                    voucher.update_totals()
                    
                    messages.success(request, f'Purchase voucher {voucher.voucher_number} created successfully!')
                    return redirect('purchase_list')
                    
            except Exception as e:
                messages.error(request, f'Error creating purchase voucher: {str(e)}')
    else:
        voucher_form = PurchaseVoucherForm()
        item_form = PurchaseItemForm()
    
    context = {
        'voucher_form': voucher_form,
        'item_form': item_form,
        'title': 'Create Purchase Voucher'
    }
    
    return render(request, 'purchases/purchase_create.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def purchase_update(request, pk):
    """Update an existing purchase voucher"""
    voucher = get_object_or_404(PurchaseVoucher, pk=pk)
    
    # Get the first item for editing (assuming single item per voucher for now)
    item = voucher.items.first()
    
    if request.method == 'POST':
        voucher_form = PurchaseVoucherForm(request.POST, instance=voucher)
        item_form = PurchaseItemForm(request.POST, request.FILES, instance=item) if item else PurchaseItemForm(request.POST, request.FILES)
        
        if voucher_form.is_valid() and item_form.is_valid():
            try:
                with transaction.atomic():
                    # Save voucher
                    voucher = voucher_form.save()
                    
                    # Save or create item
                    if item:
                        item = item_form.save()
                    else:
                        item = item_form.save(commit=False)
                        item.voucher = voucher
                        item.save()
                    
                    # Update voucher totals
                    voucher.update_totals()
                    
                    messages.success(request, f'Purchase voucher {voucher.voucher_number} updated successfully!')
                    return redirect('purchase_list')
                    
            except Exception as e:
                messages.error(request, f'Error updating purchase voucher: {str(e)}')
    else:
        voucher_form = PurchaseVoucherForm(instance=voucher)
        item_form = PurchaseItemForm(instance=item) if item else PurchaseItemForm()
    
    context = {
        'voucher_form': voucher_form,
        'item_form': item_form,
        'voucher': voucher,
        'item': item,
        'title': f'Update Purchase Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'purchases/purchase_update.html', context)


@login_required
def purchase_detail(request, pk):
    """View purchase voucher details"""
    voucher = get_object_or_404(
        PurchaseVoucher.objects.select_related('vendor').prefetch_related('items__brand', 'items__category'),
        pk=pk
    )
    
    context = {
        'voucher': voucher,
        'items': voucher.items.all(),
        'title': f'Purchase Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'purchases/purchase_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def purchase_delete(request, pk):
    """Delete a purchase voucher"""
    voucher = get_object_or_404(PurchaseVoucher, pk=pk)
    
    if request.method == 'POST':
        voucher_number = voucher.voucher_number
        try:
            voucher.delete()
            messages.success(request, f'Purchase voucher {voucher_number} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting purchase voucher: {str(e)}')
        
        return redirect('purchase_list')
    
    context = {
        'voucher': voucher,
        'title': f'Delete Purchase Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'purchases/purchase_delete.html', context)
    

@login_required
def purchase_reports(request):
    """Generate purchase reports"""
    # Date filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    vouchers = PurchaseVoucher.objects.select_related('vendor').prefetch_related('items')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate statistics
    stats = vouchers.aggregate(
        total_vouchers=Count('id'),
        total_amount=Sum('total_amount'),
        total_cost=Sum('cost'),
        total_discount=Sum('discount')
    )
    
    # Top vendors
    top_vendors = User.objects.filter(
        role='Vendor',
        purchase_vouchers__in=vouchers
    ).annotate(
        voucher_count=Count('purchase_vouchers'),
        total_spent=Sum('purchase_vouchers__total_amount')
    ).order_by('-total_spent')[:10]
    
    context = {
        'stats': stats,
        'top_vendors': top_vendors,
        'date_from': date_from,
        'date_to': date_to,
        'title': 'Purchase Reports'
    }
    
    return render(request, 'purchases/purchase_reports.html', context)


@login_required
def purchase_export(request):
    """Export purchase data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchases.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Voucher Number', 'Date', 'Vendor', 'Total Amount', 'Discount',
        'Cost', 'Payment Method', 'Payment Status', 'Status'
    ])
    
    vouchers = PurchaseVoucher.objects.select_related('vendor').all()
    
    for voucher in vouchers:
        writer.writerow([
            voucher.voucher_number,
            voucher.date,
            voucher.vendor.full_name if voucher.vendor else 'N/A',
            voucher.total_amount,
            voucher.discount,
            voucher.cost,
            voucher.get_payment_method_display(),
            voucher.get_payment_status_display(),
            voucher.get_status_display()
        ])
    
    return response

# AJAX API Views

@login_required
def update_voucher_totals(request, pk):
    """AJAX endpoint to update voucher totals"""
    if request.method == 'POST':
        voucher = get_object_or_404(PurchaseVoucher, pk=pk)
        voucher.update_totals()
        
        return JsonResponse({
            'success': True,
            'total_amount': float(voucher.total_amount),
            'cost': float(voucher.cost)
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def vendor_search(request):
    """AJAX endpoint for vendor search"""
    query = request.GET.get('q', '')
    vendors = User.objects.filter(
        role='Vendor',
        full_name__icontains=query
    )[:10]  # Limit to 10 results
    
    results = [
        {
            'id': vendor.id,
            'text': vendor.full_name,
            'username': vendor.username
        }
        for vendor in vendors
    ]
    
    return JsonResponse({'results': results})


@login_required
@csrf_exempt
def create_brand_ajax(request):
    """AJAX endpoint to create new brand"""
    if request.method == 'POST':
        data = json.loads(request.body)
        brand_name = data.get('name', '').strip()
        
        if brand_name:
            brand, created = Brand.objects.get_or_create(name=brand_name)
            return JsonResponse({
                'success': True,
                'brand': {
                    'id': brand.id,
                    'name': brand.name
                },
                'created': created
            })
        
        return JsonResponse({'success': False, 'error': 'Brand name is required'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@csrf_exempt
def create_category_ajax(request):
    """AJAX endpoint to create new category"""
    if request.method == 'POST':
        data = json.loads(request.body)
        category_name = data.get('name', '').strip()
        
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            return JsonResponse({
                'success': True,
                'category': {
                    'id': category.id,
                    'name': category.name
                },
                'created': created
            })
        
        return JsonResponse({'success': False, 'error': 'Category name is required'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def ProductList(request):
    try:
        query = request.GET.get('q', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        products =Product.objects.all().order_by('-created_at')

        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(categories__name__icontains=query)
            )

        if date_from:
            naive_date = datetime.strptime(date_from, '%Y-%m-%d')
            aware_date = timezone.make_aware(naive_date)
            products = products.filter(created_at__gte=aware_date)
        
        if date_to:
            naive_date = datetime.strptime(date_to, '%Y-%m-%d')
            aware_date = timezone.make_aware(naive_date) + timedelta(days=1)
            products = products.filter(created_at__lt=aware_date)

        paginator =Paginator(products,10)
        page_number =request.GET.get('page')
        page_obj =paginator.get_page(page_number)
        
        context ={
            "products":page_obj,
            "query": query,
            "date_from": date_from,
            "date_to": date_to
        }
        return render(request, 'product.html',context)

    except Exception as e:
        logger.error(f"Error in ProductListView: {e}")
        messages.error(request,"An error occurred while loading the product list.")
        return render(request, '404.html', {"message": "An error occurred."})
    
@login_required
@admin_required
def ProductUpdate(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)

        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('product')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProductForm(instance=product)

        return render(request, 'product_update.html', {'form': form, 'product': product})
    except Exception as e:
        logger.error(f"Error in ProductUpdateView: {e}")
        messages.error(request, 'An error occurred while updating the product.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
@admin_required
def ProductDelete(request,pk):
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

@login_required
def sales_list(request):
    """List all sales vouchers with search and filter functionality"""
    vouchers = SalesVoucher.objects.select_related('customer').prefetch_related('items').all()
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        vouchers = vouchers.filter(
            Q(voucher_number__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(items__product__name__icontains=query)
        ).distinct()
    
    # Date filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Payment status filtering
    payment_status = request.GET.get('payment_status')
    if payment_status:
        vouchers = vouchers.filter(payment_status=payment_status)
    
    # Status filtering
    status = request.GET.get('status')
    if status:
        vouchers = vouchers.filter(status=status)
    
    # Pagination
    paginator = Paginator(vouchers, 25)  # 25 vouchers per page
    page_number = request.GET.get('page')
    vouchers = paginator.get_page(page_number)
    
    # Get payment status choices for filter dropdown
    status_choices = PaymentStatusChoices.choices
    
    context = {
        'vouchers': vouchers,
        'query': query,
        'date_from': date_from,
        'date_to': date_to,
        'payment_status': payment_status,
        'status': status,
        'status_choices': status_choices,
    }
    
    return render(request, 'sales.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def sales_create(request):
    """Create a new sales voucher with items"""
    if request.method == 'POST':
        voucher_form = SalesVoucherForm(request.POST)
        item_form = SalesItemForm(request.POST)
        
        if voucher_form.is_valid() and item_form.is_valid():
            try:
                with transaction.atomic():
                    # Save voucher
                    voucher = voucher_form.save()
                    
                    # Save item and link to voucher
                    item = item_form.save(commit=False)
                    item.voucher = voucher
                    item.save()
                    
                    # Update stock
                    product = item.product
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                        product.save()
                    else:
                        raise ValueError(f"Insufficient stock for {product.name}")
                    
                    messages.success(request, f'Sales voucher {voucher.voucher_number} created successfully!')
                    return redirect('sales_list')
                    
            except Exception as e:
                messages.error(request, f'Error creating sales voucher: {str(e)}')
    else:
        voucher_form = SalesVoucherForm()
        item_form = SalesItemForm()
    
    context = {
        'voucher_form': voucher_form,
        'item_form': item_form,
        'title': 'Create Sales Voucher'
    }
    
    return render(request, 'sales/sales_create.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def sales_update(request, pk):
    """Update an existing sales voucher"""
    voucher = get_object_or_404(SalesVoucher, pk=pk)
    
    # Get the first item for editing (assuming single item per voucher for now)
    item = voucher.items.first()
    original_quantity = item.quantity if item else 0
    
    if request.method == 'POST':
        voucher_form = SalesVoucherForm(request.POST, instance=voucher)
        item_form = SalesItemForm(request.POST, instance=item) if item else SalesItemForm(request.POST)
        
        if voucher_form.is_valid() and item_form.is_valid():
            try:
                with transaction.atomic():
                    # Save voucher
                    voucher = voucher_form.save()
                    
                    # Handle item updates
                    if item:
                        # Restore original stock
                        product = item.product
                        product.stock += original_quantity
                        
                        # Update item
                        item = item_form.save()
                        
                        # Deduct new quantity from stock
                        if product.stock >= item.quantity:
                            product.stock -= item.quantity
                            product.save()
                        else:
                            raise ValueError(f"Insufficient stock for {product.name}")
                    else:
                        # Create new item
                        item = item_form.save(commit=False)
                        item.voucher = voucher
                        item.save()
                        
                        # Update stock
                        product = item.product
                        if product.stock >= item.quantity:
                            product.stock -= item.quantity
                            product.save()
                        else:
                            raise ValueError(f"Insufficient stock for {product.name}")
                    
                    messages.success(request, f'Sales voucher {voucher.voucher_number} updated successfully!')
                    return redirect('sales_list')
                    
            except Exception as e:
                messages.error(request, f'Error updating sales voucher: {str(e)}')
    else:
        voucher_form = SalesVoucherForm(instance=voucher)
        item_form = SalesItemForm(instance=item) if item else SalesItemForm()
    
    context = {
        'voucher_form': voucher_form,
        'item_form': item_form,
        'voucher': voucher,
        'item': item,
        'title': f'Update Sales Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'sales/sales_update.html', context)


@login_required
def sales_detail(request, pk):
    """View sales voucher details"""
    voucher = get_object_or_404(
        SalesVoucher.objects.select_related('customer').prefetch_related('items__product'),
        pk=pk
    )
    
    context = {
        'voucher': voucher,
        'items': voucher.items.all(),
        'title': f'Sales Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'sales/sales_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def sales_delete(request, pk):
    """Delete a sales voucher"""
    voucher = get_object_or_404(SalesVoucher, pk=pk)
    
    if request.method == 'POST':
        voucher_number = voucher.voucher_number
        try:
            with transaction.atomic():
                # Restore stock for all items
                for item in voucher.items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()
                
                voucher.delete()
                messages.success(request, f'Sales voucher {voucher_number} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting sales voucher: {str(e)}')
        
        return redirect('sales_list')
    
    context = {
        'voucher': voucher,
        'title': f'Delete Sales Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'sales/sales_delete.html', context)


# Sales Item Management Views

@login_required
def sales_items_list(request, voucher_pk):
    """List all items for a specific sales voucher"""
    voucher = get_object_or_404(SalesVoucher, pk=voucher_pk)
    items = voucher.items.select_related('product').all()
    
    context = {
        'voucher': voucher,
        'items': items,
        'title': f'Items for Sales Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'sales/sales_items_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def sales_item_create(request, voucher_pk):
    """Add a new item to an existing sales voucher"""
    voucher = get_object_or_404(SalesVoucher, pk=voucher_pk)
    
    if request.method == 'POST':
        form = SalesItemForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = form.save(commit=False)
                    item.voucher = voucher
                    item.save()
                    
                    # Update stock
                    product = item.product
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                        product.save()
                    else:
                        raise ValueError(f"Insufficient stock for {product.name}")
                    
                    # Recalculate voucher totals
                    voucher.save()
                    
                    messages.success(request, 'Item added successfully!')
                    return redirect('sales_items_list', voucher_pk=voucher.pk)
                    
            except Exception as e:
                messages.error(request, f'Error adding item: {str(e)}')
    else:
        form = SalesItemForm()
    
    context = {
        'form': form,
        'voucher': voucher,
        'title': f'Add Item to Sales Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'sales/sales_item_create.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def sales_item_update(request, voucher_pk, pk):
    """Update an existing sales item"""
    voucher = get_object_or_404(SalesVoucher, pk=voucher_pk)
    item = get_object_or_404(SalesItem, pk=pk, voucher=voucher)
    original_quantity = item.quantity
    original_product = item.product
    
    if request.method == 'POST':
        form = SalesItemForm(request.POST, instance=item)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Restore original stock
                    original_product.stock += original_quantity
                    original_product.save()
                    
                    # Save updated item
                    item = form.save()
                    
                    # Deduct new quantity from stock
                    product = item.product
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                        product.save()
                    else:
                        raise ValueError(f"Insufficient stock for {product.name}")
                    
                    # Recalculate voucher totals
                    voucher.save()
                    
                    messages.success(request, 'Item updated successfully!')
                    return redirect('sales_items_list', voucher_pk=voucher.pk)
                    
            except Exception as e:
                messages.error(request, f'Error updating item: {str(e)}')
    else:
        form = SalesItemForm(instance=item)
    
    context = {
        'form': form,
        'voucher': voucher,
        'item': item,
        'title': f'Update Item in Sales Voucher {voucher.voucher_number}'
    }
    
    return render(request, 'sales/sales_item_update.html', context)


@login_required
@require_http_methods(["POST"])
def sales_item_delete(request, voucher_pk, pk):
    """Delete a sales item"""
    voucher = get_object_or_404(SalesVoucher, pk=voucher_pk)
    item = get_object_or_404(SalesItem, pk=pk, voucher=voucher)
    
    try:
        with transaction.atomic():
            # Restore stock
            product = item.product
            product.stock += item.quantity
            product.save()
            
            item.delete()
            
            # Recalculate voucher totals
            voucher.save()
            
            messages.success(request, 'Item deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting item: {str(e)}')
    
    return redirect('sales_items_list', voucher_pk=voucher.pk)


# AJAX API Views

@login_required
def customer_search(request):
    """AJAX endpoint for customer search"""
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(
        name__icontains=query
    )[:10]  # Limit to 10 results
    
    results = [
        {
            'id': customer.id,
            'text': customer.name,
            'phone': getattr(customer, 'phone', ''),
            'email': getattr(customer, 'email', '')
        }
        for customer in customers
    ]
    
    return JsonResponse({'results': results})


@login_required
@csrf_exempt
def create_customer_ajax(request):
    """AJAX endpoint to create new customer"""
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_name = data.get('name', '').strip()
        
        if customer_name:
            customer, created = Customer.objects.get_or_create(name=customer_name)
            return JsonResponse({
                'success': True,
                'customer': {
                    'id': customer.id,
                    'name': customer.name
                },
                'created': created
            })
        
        return JsonResponse({'success': False, 'error': 'Customer name is required'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def product_search(request):
    """AJAX endpoint for product search with stock info"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(brand__name__icontains=query)
    ).select_related('brand', 'category')[:10]
    
    results = [
        {
            'id': product.id,
            'text': f"{product.name} - {product.brand.name if product.brand else 'No Brand'}",
            'stock': product.stock,
            'price': float(product.price),
            'brand': product.brand.name if product.brand else '',
            'category': product.category.name if product.category else ''
        }
        for product in products
    ]
    
    return JsonResponse({'results': results})


@login_required
def get_product_details(request, pk):
    """AJAX endpoint to get product details"""
    try:
        product = Product.objects.select_related('brand', 'category').get(pk=pk)
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'stock': product.stock,
                'warranty': product.warranty,
                'brand': product.brand.name if product.brand else '',
                'category': product.category.name if product.category else ''
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})


# Reports and Export Views

@login_required
def sales_reports(request):
    """Generate sales reports"""
    # Date filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    vouchers = SalesVoucher.objects.select_related('customer').prefetch_related('items')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate statistics
    stats = vouchers.aggregate(
        total_vouchers=Count('id'),
        total_amount=Sum('total_amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount'),
        total_discount=Sum('discount')
    )
    
    # Top customers
    top_customers = Customer.objects.filter(
        sales_vouchers__in=vouchers
    ).annotate(
        voucher_count=Count('sales_vouchers'),
        total_spent=Sum('sales_vouchers__total_amount')
    ).order_by('-total_spent')[:10]
    
    # Top products
    top_products = Product.objects.filter(
        sales_items__voucher__in=vouchers
    ).annotate(
        quantity_sold=Sum('sales_items__quantity'),
        revenue=Sum('sales_items__total_price')
    ).order_by('-revenue')[:10]
    
    context = {
        'stats': stats,
        'top_customers': top_customers,
        'top_products': top_products,
        'date_from': date_from,
        'date_to': date_to,
        'title': 'Sales Reports'
    }
    
    return render(request, 'sales/sales_reports.html', context)


@login_required
def sales_export(request):
    """Export sales data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Voucher Number', 'Date', 'Customer', 'Total Amount', 'Discount',
        'Paid Amount', 'Remaining Amount', 'Payment Method', 'Payment Status', 'Status'
    ])
    
    vouchers = SalesVoucher.objects.select_related('customer').all()
    
    for voucher in vouchers:
        writer.writerow([
            voucher.voucher_number,
            voucher.date,
            voucher.customer.name if voucher.customer else 'N/A',
            voucher.total_amount,
            voucher.discount,
            voucher.paid_amount,
            voucher.remaining_amount,
            voucher.get_payment_method_display(),
            voucher.get_payment_status_display(),
            voucher.get_status_display()
        ])
    
    return response


@login_required
def RepairList(request):
    try:
        query = request.GET.get('q', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        status_filter = request.GET.get('status', '')
        payment_status_filter = request.GET.get('payment_status', '')

        repairs=Repair.objects.all().order_by('id')

        if query:
            repairs = repairs.filter(
                Q(user__full_name__icontains=query) | 
                Q(device_model__icontains=query) |    
                Q(payment_status__icontains=query) 
            )
        if start_date:
            repairs = repairs.filter(created_at__gte=start_date)
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            repairs = repairs.filter(created_at__lte=end_date_obj)
        if status_filter:
            repairs = repairs.filter(status=status_filter)
        if payment_status_filter: 
            repairs = repairs.filter(payment_status=payment_status_filter)

        pagination=Paginator(repairs,10)
        page_number=request.GET.get('page')
        page_obj=pagination.get_page(page_number)
        context={
            'repair':page_obj,
            'query': query,
            'status_choices': Repair.STATUS_CHOICES,
            'status_filter': status_filter,
            'payment_status_choices': PaymentStatusChoices.choices,
            'payment_status_filter': payment_status_filter, 
            'start_date': start_date,                
            'end_date': end_date,
        }
        return render(request, 'repair.html',context)
    except Exception as e:
        logger.error(f'An error occurred while loading the repair list:- {e}')
        messages.error(request, 'An error occurred while loading the repair list.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def RepairCreate(request,repair_id=None):
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
                print("Form Errors:", form.errors) 
                messages.error(request, 'Form is invalid.')
        return render(request, 'repair_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in RepairCreateView: {e}")
        messages.error(request, 'An error occurred while processing the repair.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def RepairUpdate(request,pk):
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

@login_required
@admin_required
def RepairDelete(request,pk):
    try:
        repair=get_object_or_404(Repair,pk=pk)
        if request.method == 'POST':
            repair_name=repair.product_name
            repair.delete()
            messages.success(request,f'Repair {repair_name} deleted successfully!')
            return redirect('repair')
        return render(request, 'repair_delete.html',{'repair':repair})
    except Exception as e:
        logger.error(f"Error in RepairDeleteView{pk}: {e}")
        messages.error(request, 'An error occurred while processing the repair.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def RepairDetailList(request):
    try:
        query = request.GET.get('q', '')
        repairdetail = RepairDetail.objects.all().order_by('id')

        if query:
            repairdetail = repairdetail.filter(
                Q(repair_order__product_name__icontains=query) | 
                Q(fixed_description__icontains=query) |  
                Q(repair_action__icontains=query) 
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

@login_required
def RepairDetailUpdate(request,pk):
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
    
@login_required   
@admin_required 
def RepairDetailDelete(request, pk):
    try:
        repairdetail = get_object_or_404(RepairDetail, pk=pk)

        if request.method == 'POST':
            repairdetail_name = repairdetail.product_name
            repairdetail.delete()
            messages.success(request, f"Repair Detail '{repairdetail_name}' deleted successfully!")
            return redirect('repair_detail')  
        return render(request, 'repair_detail_delete.html', {'repairdetail': repairdetail, 'deleted': False})

    except Exception as e:
        logger.error(f"Error in RepairDetailDeleteView: {e}", exc_info=True)
        messages.error(request, 'An error occurred while processing the repair detail. Please try again later.')
        return render(request, '404.html', {"message": "An error occurred."})
    
@login_required
def ExpenseList(request):
    try:
        query = request.GET.get('search', '')
        expenses = Expense.objects.filter(description__icontains=query) if query else Expense.objects.all()
        paginator = Paginator(expenses, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'expense.html', {'expenses': page_obj, 'query': query})
    except Exception as e:
        logger.error(f"Error occurred while fetching expenses: {e}", exc_info=True)
        return render(request, 'error.html', {'message': 'An error occurred while fetching expenses.'})


@login_required
def ExpenseCreate(request,expense_id=None):
    try:
        if expense_id:
            expense=get_object_or_404(Expense,id=expense_id)
            form=ExpenseForm(request.POST or None,instance=expense)
            action='update'
        else:
            form=ExpenseForm(request.POST or None)
            action='create'
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request,f'Expense {action.lower()}d successfully!')
                return redirect('expense')
            else:
                messages.error(request, 'Expense Form is invalid.')
        return render(request, 'expense_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in Expense Create: {e}")
        messages.error(request, 'An error occurred while processing the Expense Create.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def ExpenseUpdate(request,pk):
    try:
        expense=get_object_or_404(Expense,pk=pk)
        if request.method == 'POST':
            form=ExpenseForm(request.POST or None,instance=expense)
            if form.is_valid():
                form.save()
                messages.success(request,f'Expense updated successfully!')
                return redirect('expense')
        else:
            form =ExpenseForm(instance=expense)
            return render(request, 'expense_update.html', {'form': form, 'expenses': expense})
    except Exception as e:
        logger.error(f"Error in Expense Update: {e}")
        messages.error(request, 'An error occurred while processing the expense.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def ExpenseDelete(request,pk):
    try:
        expense= get_object_or_404(Expense,pk=pk)
        if request.method == 'POST':
            expense=expense.category.name
            expense.delete()
            messages.success(request,f'Expense {expense} deleted successfully!')
            return redirect('expense')
        return render(request, 'expense_delete.html',{'expenses':expense})
    except Exception as e:
        logger.error(f"Error in ExpenseDelete: {e}")
        messages.error(request, 'An error occurred while processing the Expense Delete.')
        return render(request, '404.html', {"message": "An error occurred Expense Delete."})

@login_required
def SalesInvoiceList(request):
    query = request.GET.get('search', '')
    invoices = SalesInvoice.objects.filter(
        invoice_number__icontains=query
        ) if query else SalesInvoice.objects.all()

    paginator = Paginator(invoices, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = ({            
            'invoices': page_obj,
            'query': query
        })
    return render(request, 'sales_invoice.html', context)
    
@login_required
def SalesInvoiceUpdate(request, pk):
    try:
        salesinvoice = get_object_or_404(SalesInvoice, pk=pk)
        if request.method == 'POST':
            form = SalesInvoiceForm(request.POST, instance=salesinvoice)
            if form.is_valid():
                form.save()
                messages.success(request, 'Sales Invoice updated successfully!')
                return redirect('salesinvoice')
        else:
            form = SalesInvoiceForm(instance=salesinvoice)
        return render(request, 'sales_invoice_update.html', {'form': form, 'salesinvoice': salesinvoice})
    except Exception as e:
        logger.error(f"Error in Sales Invoice: {e}")
        messages.error(request, 'An error occurred while processing the Sales Invoice.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def RepairInvoiceList(request):
    query = request.GET.get('search', '')
    repair_invoices = RepairInvoice.objects.filter(
        invoice_number__icontains=query
    ) if query else RepairInvoice.objects.all()

    paginator = Paginator(repair_invoices, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'invoices': page_obj,
        'query': query,
    }
    return render(request, 'repair_invoice.html', context)

@login_required
def RepairInvoiceUpdate(request, pk):
    try:
        repair_invoice = get_object_or_404(RepairInvoice, pk=pk)

        if request.method == 'POST':
            form = RepairInvoiceForm(request.POST, instance=repair_invoice)
            if form.is_valid():
                form.save()
                messages.success(request, 'Repair Invoice updated successfully!')
                return redirect('repairinvoice')
        else:
            form = RepairInvoiceForm(instance=repair_invoice)
        return render(request, 'repair_invoice_update.html', {'form': form, 'repair_invoice': repair_invoice})
    except Exception as e:
        logger.error(f"Error in Repair Invoice: {e}")
        messages.error(request, 'An error occurred while processing the Repair Invoice.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def ReturnList(request):
    query = request.GET.get('search', '')
    if query:
        returns = Return.objects.filter(
            Q(invoice__invoice_number__icontains=query) | 
            Q(product__name__icontains=query) | 
            Q(customer_name__icontains=query)
        )
    else:
        returns = Return.objects.all()

    paginator = Paginator(returns, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'return.html', {
        'returns': page_obj,
        'query': query
    })


@login_required
def ReturnCreate(request,return_id=None):
    try:
        if return_id:
            returns=get_object_or_404(Return,id=return_id)
            form=ReturnForm(request.POST or None,instance=returns)
            action='update'
        else:
            form=ReturnForm(request.POST or None)
            action='create'
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request,f'Return {action.lower()}d successfully!')
                return redirect('return')
            else:
                messages.error(request, 'Return Form is invalid.')
        return render(request, 'return_create.html',{'form':form,'action':action})
    except Exception as e:
        logger.error(f"Error in Return Create: {e}")
        messages.error(request, 'An error occurred while processing the Return Create.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def ReturnUpdate(request,pk):
    try:
        returns=get_object_or_404(Return,pk=pk)
        if request.method == 'POST':
            form=ReturnForm(request.POST or None,instance=returns)
            if form.is_valid():
                form.save()
                messages.success(request,f'Return updated successfully!')
                return redirect('return')
        else:
            form =ReturnForm(instance=returns)
            return render(request, 'return_update.html', {'form': form, 'returns': returns})
    except Exception as e:
        logger.error(f"Error in Return Update: {e}")
        messages.error(request, 'An error occurred while processing the Return.')
        return render(request, '404.html', {"message": "An error occurred."})


@login_required
def ReturnDelete(request, pk):
    try:
        returns = get_object_or_404(Return, pk=pk) 
        invoice_number = returns.invoice.invoice_number

        if request.method == 'POST':
            returns.delete() 
            messages.success(request, f'Return {invoice_number} deleted successfully!')
            return redirect('return')

        return render(request, 'return_delete.html', {'returns': returns})

    except Exception as e:
        logger.error(f"Error in Return Delete: {e}")
        messages.error(request, 'An error occurred while processing the Return Delete.')
        return render(request, '404.html', {"message": "An error occurred Return Delete."})

@login_required
def UserReportList(request):
    try:
        selected_role = request.GET.get('role', '') 
        users = User.objects.all().order_by('id')

        if selected_role:
            users = users.filter(role=selected_role)

        customer_count = users.filter(role='Customer').count()
        vendor_count = users.filter(role='Vendor').count()
        active_users = users.filter(is_active=True).count()
        inactive_users = users.filter(is_active=False).count()
        role_chart_data = {
            'labels': ['Customers', 'Vendors'],
            'data': [customer_count, vendor_count] if customer_count or vendor_count else [0, 0]
        }
        status_chart_data = {
            'labels': ['Active', 'Inactive'],
            'data': [active_users, inactive_users] if active_users or inactive_users else [0, 0]
        }

        pagination = Paginator(users, 10)
        page_number = request.GET.get('page')
        page_obj = pagination.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'selected_role': selected_role,
            'customer_count': customer_count,
            'vendor_count': vendor_count,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'role_chart_data': role_chart_data,
            'status_chart_data': status_chart_data,

        }
        return render(request, 'user_report.html', context)

    except Exception as e:
        logger.error(f"Error in UserReportListView: {e}")
        messages.error(request, 'An error occurred while loading the report list.')
        return render(request, '404.html', {"message": "An error occurred."})

@login_required
def global_search(request):
    query = request.GET.get('q')
    context = {'query': query}

    try:
        if query:
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(categories__name__icontains=query)
            ).distinct()
            sales = Sales.objects.filter(
                Q(user__full_name__icontains=query) |
                Q(product__name__icontains=query) |
                Q(payment_status__icontains=query) |
                Q(Imei__icontains=query)
            ).distinct()


            purchases = Purchase.objects.filter(
                Q(vendor__full_name__icontains=query) |
                Q(product_name__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(Imei__icontains=query)
            ).distinct()


            repairs = Repair.objects.filter(
                Q(user__full_name__icontains=query) |
                Q(device_model__icontains=query) |
                Q(payment_status__icontains=query) |
                Q(product_name__icontains=query)
            ).distinct()

            brands = Brand.objects.filter(
                Q(name__icontains=query)
            ).distinct()


            categories = Category.objects.filter(
                Q(name__icontains=query)
            ).distinct()


            users = User.objects.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            ).distinct()
        
            expenses = Expense.objects.filter(
                Q(category__name__icontains=query) |
                Q(description__icontains=query) |
                Q(payment_status__icontains=query)
            ).distinct()

            sales_invoices = SalesInvoice.objects.filter(
                Q(customer_name__icontains=query) |
                Q(invoice_number__icontains=query) |
                Q(product_name__icontains=query)
            ).distinct()

            repair_invoices = RepairInvoice.objects.filter(
                Q(customer_name__icontains=query) |
                Q(invoice_number__icontains=query) |
                Q(product_name__icontains=query)
            ).distinct()


            # Companies search
            companies = Company.objects.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone_number__icontains=query)
            ).distinct().order_by('-created_at')


            context.update({
                'products': products,
                'sales': sales,
                'purchases': purchases,
                'repairs': repairs,
                'brands': brands,
                'categories': categories,
                'companies':companies,
                'users': users,
                'expenses': expenses,
                'sales_invoices': sales_invoices,
                'repair_invoices': repair_invoices,
            })
    except Exception as e:
        logger.error(f"Error occurred in global_search: {e}", exc_info=True)
        context['error'] = "An error occurred while processing your search. Please try again."

    return render(request, 'search_results.html', context)

@login_required
def SalesReportList(request):
    context = {}
    try:
        sales = Sales.objects.all()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            sales = sales.filter(created_at__date__range=[start_date, end_date])
        total_quantity = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_sales = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        daily_sales = sales.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            daily_total=Sum('total_amount')
        ).order_by('day')
        
        payment_methods = sales.values('payment_method').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')

        context = {
            'sales': sales,
            'total_quantity': total_quantity,
            'total_sales': total_sales,
            'daily_sales': json.dumps([
                {
                    'day': item['day'].isoformat(),
                    'daily_total': float(item['daily_total'])
                } for item in daily_sales
            ]),
            'payment_methods': json.dumps([
                {
                    'method': item['payment_method'],
                    'total': float(item['total']),
                    'count': item['count']
                } for item in payment_methods
            ]),
        }
    
    except Exception as e:
        logger.error(f"Error occurred in SalesReportListView: {e}", exc_info=True)
        context['error'] = "An error occurred while generating the sales report."

    return render(request, 'sales_report.html', context)


@login_required
def sales_excel(request):
    sales = Sales.objects.all().select_related('product', 'user')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    headers = [
        "ID", "Product", "IMEI", "Customer", "Quantity", "Price", "Discount", "Total Amount",
        "Paid", "Remaining", "Payment Method", "Payment Status", "Warranty",
        "Due Date", "Notes", "Created At"
    ]
    ws.append(headers)

    for col in ws.iter_cols(min_row=1, max_row=1):
        for cell in col:
            cell.font = Font(bold=True)

    for sale in sales:
        ws.append([
            sale.id,
            sale.product.name if sale.product else 'N/A',
            sale.Imei or '',
            sale.user.full_name if sale.user else 'N/A', 
            sale.quantity,
            sale.price or 0, 
            sale.discount or 0, 
            sale.total_amount or 0, 
            sale.paid_amount or 0, 
            sale.remaining_amount or 0,
            sale.payment_method,
            sale.payment_status,
            sale.warranty or 0, 
            sale.due_date.strftime('%Y-%m-%d') if sale.due_date else '',
            sale.notes or '',
            localtime(sale.created_at).strftime('%Y-%m-%d %H:%M') if sale.created_at else '',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=SalesReport.xlsx'
    
    wb.save(response)
    return response

@login_required
def StockReportList(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product_name = request.GET.get('product_name')
    low_stock_threshold = request.GET.get('low_stock_threshold')
    total_sales_threshold = request.GET.get('total_sales_threshold')

    products = Product.objects.all()

    if start_date:
        products = products.filter(created_at__gte=start_date)
    if end_date:
        products = products.filter(created_at__lte=end_date)
    if product_name:
        products = products.filter(name__icontains=product_name)
    if low_stock_threshold:
        products = products.filter(stock__lt=low_stock_threshold)
    if total_sales_threshold:
        products = products.annotate(
            total_sales=Sum('sales__quantity') 
        ).filter(total_sales__gte=total_sales_threshold)

    sales_data = Sales.objects.filter(product__in=products).values('product').annotate(total_sales=Sum('quantity'))
    purchases_data = Purchase.objects.filter(product_name__in=products.values_list('name', flat=True))\
    .values('product_name').annotate(total_purchased=Sum('quantity'))
    sales_dict = {sale['product']: sale['total_sales'] for sale in sales_data}
    purchases_dict = {purchase['product_name']: purchase['total_purchased'] for purchase in purchases_data}

    for product in products:
        product.total_sales = sales_dict.get(product.id, 0)
        product.total_purchased = purchases_dict.get(product.name, 0)

    context = {
        'products': products,
        'start_date': start_date,
        'end_date': end_date,
        'product_name': product_name,
        'low_stock_threshold': low_stock_threshold,
        'total_sales_threshold': total_sales_threshold,
    }

    return render(request, 'stock_report.html', context)


@login_required
def stock_excel(request):
    try:
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        product_name = request.GET.get("product_name")
        
        products = Product.objects.select_related('categories').all()
        if product_name:
            products = products.filter(name__icontains=product_name)
        
        sales = Sales.objects.select_related('product')
        purchases = Purchase.objects.all() 

        parsed_start_date = None
        parsed_end_date = None

        if start_date and end_date:
            date_format = "%Y-%m-%d"
            try:
                parsed_start_date = datetime.strptime(start_date, date_format).date()
                parsed_end_date = datetime.strptime(end_date, date_format).date()
                
                if parsed_start_date > parsed_end_date:
                    messages.error(request, "Start date must be before or equal to end date")
                    return redirect('stock_report')
                
                sales = sales.filter(created_at__date__range=[parsed_start_date, parsed_end_date])
                purchases = purchases.filter(created_at__date__range=[parsed_start_date, parsed_end_date])
                
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('stock_report')

        sales_totals = sales.values('product_id').annotate(total_sold=Sum('quantity'))
        sales_dict = {item['product_id']: item['total_sold'] or 0 for item in sales_totals}

        purchases_totals = purchases.values('product_name').annotate(total_purchased=Sum('quantity'))
        purchases_dict = {item['product_name']: item['total_purchased'] or 0 for item in purchases_totals}

        wb = Workbook()
        ws = wb.active
        ws.title = "Stock Report"

        headers = ["ID", "Product Name", "Category", "Stock", "Sold", "Purchased", "Created Date"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", fill_type="solid")

        for product in products:
            try:
                total_sold = sales_dict.get(product.id, 0)
                total_purchased = purchases_dict.get(product.name, 0) 
                created_date = product.created_at.strftime("%Y-%m-%d") if product.created_at else "N/A"

                ws.append([
                    product.id,
                    product.name,
                    product.categories.name if product.categories else "No Category",
                    product.stock,
                    total_sold,
                    total_purchased,
                    created_date
                ])
            except Exception as e:
                logger.error(f"Error processing product {product.id}: {e}")
                continue

        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            ws.column_dimensions[col_letter].width = max_length + 2

        filename = f"stock_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        wb.save(response)
        return response

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        messages.error(request, "Failed to generate Excel report.")
        return redirect('stock_report')

@login_required
def RepairReportList(request):
    try:
        status = request.GET.get('status', '')  
        customer_id = request.GET.get('customer', '')  
        repairs = Repair.objects.all().order_by('-created_at')  
        if status:
            repairs = repairs.filter(status=status)
        if customer_id:
            repairs = repairs.filter(name_id=customer_id) 
        status_counts = repairs.values('status').annotate(
            count=Count('id'),
            percentage=Count('id') * 100.0 / repairs.count()
        ).order_by('-count')
        daily_repairs = repairs.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        status_data = list(status_counts)
        daily_data = list(daily_repairs)

        paginator = Paginator(repairs, 10)
        page_number = request.GET.get('page')

        try:
            repairs_page = paginator.get_page(page_number)
        except Exception as e:
            logger.warning(f"Pagination error: {e}")
            repairs_page = paginator.get_page(1)  

        customers = User.objects.filter(role="Customer").order_by('full_name')

        context = {
            'repairs': repairs_page,
            'customers': customers,
            'selected_status': status,
            'selected_customer': customer_id,
            'status_data': json.dumps(status_data),
            'daily_data': json.dumps(daily_data, default=str),
        }
        logger.info("Repair report generated successfully.")
    except Exception as e:
        logger.error(f"Error in RepairReportListView: {e}", exc_info=True)
        context = {"error": "An error occurred while generating the repair report."}
    return render(request, 'repair_report.html', context)

@login_required
def RepairDetailReportList(request):
    try:
        repair_order_id = request.GET.get('repair_order', '')  
        repair_action = request.GET.get('repair_action', '')  

        repair_details = RepairDetail.objects.select_related('repair_order').order_by('-created_at')

        if repair_order_id:
            repair_details = repair_details.filter(repair_order_id=repair_order_id)
        if repair_action:
            repair_details = repair_details.filter(repair_action=repair_action)

        paginator = Paginator(repair_details, 10)
        page_number = request.GET.get('page')

        try:
            repair_details_page = paginator.get_page(page_number)
        except Exception as e:
            logger.warning(f"Pagination error in RepairDetailReportListView: {e}")
            repair_details_page = paginator.get_page(1)  

        repair_orders = Repair.objects.all().order_by('-created_at')

        context = {
            'repair_details': repair_details_page,
            'repair_orders': repair_orders,
            'selected_repair_order': repair_order_id,
            'selected_repair_action': repair_action,
        }

        logger.info("Repair detail report generated successfully.")

    except Exception as e:
        logger.error(f"Error in RepairDetailReportListView: {e}", exc_info=True)
        context = {"error": "An error occurred while generating the repair detail report."}

    return render(request, 'repair_detail_report.html', context)

@login_required
def generate_sales_invoice(request, pk):
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    company = Company.objects.first()
    context={
        'invoice': invoice,
        'company': company
        }
    return render(request, 'salesinvoiceprint.html',context)

@login_required
def generate_repair_invoice(request, pk):
    invoice = get_object_or_404(RepairInvoice, pk=pk)
    company = Company.objects.first()  
    
    context={
        'invoice': invoice,
        'company': company
        }
    return render(request, 'repairinvoiceprint.html',context)


def stock_ledger_list(request):
    query = request.GET.get('query', '')
    
    ledger_entries = StockLedger.objects.select_related('product', 'created_by').order_by('-transaction_date')
    
    if query:
        ledger_entries = ledger_entries.filter(
            Q(product__name__icontains=query) |
            Q(transaction_type__icontains=query) |
            Q(notes__icontains=query)
        )
    
    paginator = Paginator(ledger_entries, 25)  # Show 25 entries per page
    page_number = request.GET.get('page')
    stock_ledger = paginator.get_page(page_number)
    
    context = {
        'stock_ledger': stock_ledger,
        'query': query,
    }
    return render(request, 'stock_ledger.html', context)

def stock_ledger_create(request):
    if request.method == 'POST':
        form = StockLedgerForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            messages.success(request, 'Stock ledger entry created successfully!')
            return redirect('stock_ledger')
    else:
        form = StockLedgerForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'stock_ledger_form.html', context)

def stock_ledger_update(request, pk):
    entry = get_object_or_404(StockLedger, pk=pk)
    
    if request.method == 'POST':
        form = StockLedgerForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock ledger entry updated successfully!')
            return redirect('stock_ledger')
    else:
        form = StockLedgerForm(instance=entry, user=request.user)
    
    context = {'form': form, 'entry': entry}
    return render(request, 'stock_ledger_form.html', context)

def stock_ledger_delete(request, pk):
    entry = get_object_or_404(StockLedger, pk=pk)
    
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Stock ledger entry deleted successfully!')
        return redirect('stock_ledger')
    
    context = {'entry': entry}
    return render(request, 'stock_ledger_confirm_delete.html', context)


def daybook_list(request):
    query = request.GET.get('query', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    transaction_type = request.GET.get('transaction_type', '')
    
    entries = Daybook.objects.select_related('created_by').order_by('-date')
    
    if query:
        entries = entries.filter(
            Q(description__icontains=query) |
            Q(reference_id__icontains=query) |
            Q(reference_model__icontains=query)
        )
    
    if date_from:
        entries = entries.filter(date__gte=date_from)
    
    if date_to:
        entries = entries.filter(date__lte=date_to)
    
    if transaction_type:
        entries = entries.filter(transaction_type=transaction_type)
    
    paginator = Paginator(entries, 25)  # Show 25 entries per page
    page_number = request.GET.get('page')
    daybook = paginator.get_page(page_number)
    
    context = {
        'daybook': daybook,
        'query': query,
        'date_from': date_from,
        'date_to': date_to,
        'transaction_type': transaction_type,
        'transaction_types': Daybook.TRANSACTION_TYPES,
    }
    return render(request, 'daybook_list.html', context)

def daybook_create(request):
    if request.method == 'POST':
        form = DaybookForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            messages.success(request, 'Daybook entry created successfully!')
            return redirect('daybook_list')
    else:
        form = DaybookForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'daybook_form.html', context)

def daybook_update(request, pk):
    entry = get_object_or_404(Daybook, pk=pk)
    
    if request.method == 'POST':
        form = DaybookForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Daybook entry updated successfully!')
            return redirect('daybook_list')
    else:
        form = DaybookForm(instance=entry, user=request.user)
    
    context = {'form': form, 'entry': entry}
    return render(request, 'daybook_form.html', context)

def daybook_delete(request, pk):
    entry = get_object_or_404(Daybook, pk=pk)
    
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Daybook entry deleted successfully!')
        return redirect('daybook_list')
    
    context = {'entry': entry}
    return render(request, 'daybook_confirm_delete.html', context)


@login_required
def cashbook_list(request):
    try:
        query = request.GET.get('query', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        entry_type = request.GET.get('entry_type', '')
        is_bank = request.GET.get('is_bank', '')
        
        entries = Cashbook.objects.select_related('recorded_by').order_by('-transaction_date', '-date')
        
        if query:
            entries = entries.filter(
                Q(description__icontains=query) |
                Q(reference_id__icontains=query) |
                Q(reference_model__icontains=query) |
                Q(cheque_number__icontains=query))
        
        if date_from:
            entries = entries.filter(transaction_date__gte=date_from)
        
        if date_to:
            entries = entries.filter(transaction_date__lte=date_to)
        
        if entry_type:
            entries = entries.filter(entry_type=entry_type)
        
        if is_bank in ['true', 'false']:
            entries = entries.filter(is_bank=(is_bank == 'true'))
        
        paginator = Paginator(entries, 25)
        page_number = request.GET.get('page')
        
        try:
            cashbook = paginator.page(page_number)
        except PageNotAnInteger:
            cashbook = paginator.page(1)
        except EmptyPage:
            cashbook = paginator.page(paginator.num_pages)
        
        context = {
            'cashbook': cashbook,
            'query': query,
            'date_from': date_from,
            'date_to': date_to,
            'entry_type': entry_type,
            'is_bank': is_bank,
            'entry_types': Cashbook.ENTRY_TYPES,
            'source_types': Cashbook.SOURCE_TYPES,
        }
        return render(request, 'cashbook_list.html', context)
    
    except Exception as e:
        messages.error(request, f"An error occurred while loading cashbook entries: {str(e)}")
        return render(request, 'cashbook_list.html', {'cashbook': []})

@login_required
def cashbook_create(request):
    try:
        if request.method == 'POST':
            form = CashbookForm(request.POST, user=request.user)
            if form.is_valid():
                entry = form.save(commit=False)
                entry.recorded_by = request.user
                entry.save()
                messages.success(request, 'Cashbook entry created successfully!')
                return redirect('cashbook_list')
        else:
            form = CashbookForm(user=request.user)
        
        context = {'form': form}
        return render(request, 'cashbook_form.html', context)
    
    except ValidationError as e:
        messages.error(request, f"Validation error: {str(e)}")
        return redirect('cashbook_create')
    except Exception as e:
        messages.error(request, f"An error occurred while creating cashbook entry: {str(e)}")
        return render(request, 'cashbook_form.html', {'form': CashbookForm(user=request.user)})

@login_required
def cashbook_update(request, pk):
    try:
        entry = get_object_or_404(Cashbook, pk=pk)
        
        if request.method == 'POST':
            form = CashbookForm(request.POST, instance=entry, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Cashbook entry updated successfully!')
                return redirect('cashbook_list')
        else:
            form = CashbookForm(instance=entry, user=request.user)
        
        context = {'form': form, 'entry': entry}
        return render(request, 'cashbook_form.html', context)
    
    except ValidationError as e:
        messages.error(request, f"Validation error: {str(e)}")
        return redirect('cashbook_update', pk=pk)
    except Exception as e:
        messages.error(request, f"An error occurred while updating cashbook entry: {str(e)}")
        return redirect('cashbook_list')

@login_required
def cashbook_delete(request, pk):
    try:
        entry = get_object_or_404(Cashbook, pk=pk)
        
        if request.method == 'POST':
            entry_description = str(entry)
            entry.delete()
            messages.success(request, f'Cashbook entry "{entry_description}" deleted successfully!')
            return redirect('cashbook_list')
        
        context = {'entry': entry}
        return render(request, 'cashbook_confirm_delete.html', context)
    
    except Exception as e:
        messages.error(request, f"An error occurred while deleting cashbook entry: {str(e)}")
        return redirect('cashbook_list')
