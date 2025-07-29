from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
import logging
from .models import *

logger = logging.getLogger(__name__)

# Global flag to prevent infinite loops
_signal_processing = set()

def prevent_infinite_loop(signal_name, instance_id):
    """Decorator to prevent infinite signal loops"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = f"{signal_name}_{instance_id}"
            if key in _signal_processing:
                logger.debug(f"Preventing infinite loop for {key}")
                return
            
            _signal_processing.add(key)
            try:
                return func(*args, **kwargs)
            finally:
                _signal_processing.discard(key)
        return wrapper
    return decorator

# ==================== VOUCHER NUMBER GENERATION ====================

@receiver(pre_save, sender=PurchaseVoucher)
def generate_purchase_voucher_number(sender, instance, **kwargs):
    """Generate unique voucher number with proper error handling"""
    if instance.voucher_number:
        return  # Already has a number
        
    try:
        # The model's save method handles voucher number generation
        # Signal just ensures it happens
        pass
    except Exception as e:
        logger.error(f"Error in purchase voucher number generation: {e}")
        raise ValidationError(f"Failed to generate voucher number: {e}")

@receiver(pre_save, sender=SalesVoucher)
def generate_sales_voucher_number(sender, instance, **kwargs):
    """Generate unique voucher number with proper error handling"""
    if instance.voucher_number:
        return  # Already has a number
        
    try:
        # The model's save method handles voucher number generation
        # Signal just ensures it happens
        pass
    except Exception as e:
        logger.error(f"Error in sales voucher number generation: {e}")
        raise ValidationError(f"Failed to generate voucher number: {e}")

# ==================== STOCK MANAGEMENT SIGNALS ====================

@receiver(post_save, sender=PurchaseItem)
def handle_purchase_item_stock(sender, instance, created, **kwargs):
    """Handle stock updates for purchase items using StockLedger"""
    if not created:
        return  # Only handle new items to avoid complications
    
    signal_key = f"purchase_stock_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            # Get or create product
            product, product_created = Product.objects.get_or_create(
                name=instance.product_name,
                defaults={
                    'vendor': instance.voucher.vendor,
                    'price': instance.price,
                    'brand': instance.brand,
                    'categories': instance.category,
                    'warranty': instance.warranty,
                    'stock': 0,
                    'description': instance.description or ''
                }
            )
            
            # Update product details if it already existed
            if not product_created:
                updated_fields = []
                if product.price != instance.price:
                    product.price = instance.price
                    updated_fields.append('price')
                if instance.warranty and product.warranty != instance.warranty:
                    product.warranty = instance.warranty
                    updated_fields.append('warranty')
                if instance.brand and product.brand != instance.brand:
                    product.brand = instance.brand
                    updated_fields.append('brand')
                if instance.category and product.categories != instance.category:
                    product.categories = instance.category
                    updated_fields.append('categories')
                
                if updated_fields:
                    product.save(update_fields=updated_fields)
            
            # Create stock ledger entry (this updates product stock automatically)
            StockLedger.create_entry(
                product=product,
                transaction_type='purchase',
                reference_id=instance.voucher.id,
                reference_model='PurchaseVoucher',
                quantity=instance.quantity,
                unit_cost=instance.price,
                created_by=instance.voucher.vendor,
                notes=f"Purchase item from voucher {instance.voucher.voucher_number}"
            )
            
            logger.info(f"Stock updated for product {product.name}: +{instance.quantity}")
            
    except Exception as e:
        logger.error(f"Error handling purchase item stock for item {instance.pk}: {e}")
        raise
    finally:
        _signal_processing.discard(signal_key)

@receiver(post_save, sender=SalesItem)
def handle_sales_item_stock(sender, instance, created, **kwargs):
    """Handle stock updates for sales items using StockLedger"""
    if not created:
        return  # Only handle new items
    
    signal_key = f"sales_stock_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            # Create stock ledger entry (negative quantity for sale)
            StockLedger.create_entry(
                product=instance.product,
                transaction_type='sale',
                reference_id=instance.voucher.id,
                reference_model='SalesVoucher',
                quantity=-instance.quantity,  # Negative for outgoing stock
                unit_cost=instance.product.price,  # Use product's cost price
                created_by=getattr(instance.voucher, 'created_by', None),
                notes=f"Sale item from voucher {instance.voucher.voucher_number}"
            )
            
            logger.info(f"Stock updated for product {instance.product.name}: -{instance.quantity}")
            
    except ValidationError as e:
        logger.error(f"Stock validation error for sales item {instance.pk}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error handling sales item stock for item {instance.pk}: {e}")
        raise
    finally:
        _signal_processing.discard(signal_key)

@receiver(pre_delete, sender=PurchaseItem)
def handle_purchase_item_delete(sender, instance, **kwargs):
    """Handle stock restoration when purchase items are deleted"""
    signal_key = f"purchase_delete_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        # Find the corresponding product
        products = Product.objects.filter(name=instance.product_name)
        if not products.exists():
            logger.warning(f"No product found for deleted purchase item: {instance.product_name}")
            return
        
        product = products.first()
        
        with transaction.atomic():
            # Create negative stock ledger entry to reverse the purchase
            StockLedger.create_entry(
                product=product,
                transaction_type='adjustment',
                reference_id=instance.voucher.id,
                reference_model='PurchaseVoucher',
                quantity=-instance.quantity,  # Negative to reduce stock
                unit_cost=instance.price,
                created_by=instance.voucher.vendor,
                notes=f"Reversal: Purchase item deleted from voucher {instance.voucher.voucher_number}"
            )
            
            logger.info(f"Stock restored for product {product.name}: -{instance.quantity}")
            
    except Exception as e:
        logger.error(f"Error handling purchase item deletion for item {instance.pk}: {e}")
        # Don't raise here as it would prevent deletion
    finally:
        _signal_processing.discard(signal_key)

@receiver(pre_delete, sender=SalesItem)
def handle_sales_item_delete(sender, instance, **kwargs):
    """Handle stock restoration when sales items are deleted"""
    signal_key = f"sales_delete_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            # Create positive stock ledger entry to restore the stock
            StockLedger.create_entry(
                product=instance.product,
                transaction_type='adjustment',
                reference_id=instance.voucher.id,
                reference_model='SalesVoucher',
                quantity=instance.quantity,  # Positive to restore stock
                unit_cost=instance.product.price,
                created_by=getattr(instance.voucher, 'created_by', None),
                notes=f"Reversal: Sales item deleted from voucher {instance.voucher.voucher_number}"
            )
            
            logger.info(f"Stock restored for product {instance.product.name}: +{instance.quantity}")
            
    except Exception as e:
        logger.error(f"Error handling sales item deletion for item {instance.pk}: {e}")
        # Don't raise here as it would prevent deletion
    finally:
        _signal_processing.discard(signal_key)

# ==================== VOUCHER TOTALS UPDATE ====================

@receiver([post_save, post_delete], sender=PurchaseItem)
def update_purchase_voucher_totals_signal(sender, instance, **kwargs):
    """Update purchase voucher totals when items change"""
    if not hasattr(instance, 'voucher') or not instance.voucher:
        return
    
    signal_key = f"purchase_totals_{instance.voucher.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        # Use the model's update_totals method
        instance.voucher.update_totals()
        logger.debug(f"Updated totals for purchase voucher {instance.voucher.voucher_number}")
    except Exception as e:
        logger.error(f"Error updating purchase voucher totals: {e}")
    finally:
        _signal_processing.discard(signal_key)

@receiver([post_save, post_delete], sender=SalesItem)
def update_sales_voucher_totals_signal(sender, instance, **kwargs):
    """Update sales voucher totals when items change"""
    if not hasattr(instance, 'voucher') or not instance.voucher:
        return
    
    signal_key = f"sales_totals_{instance.voucher.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        # Trigger the voucher's save method to recalculate totals
        instance.voucher.save()
        logger.debug(f"Updated totals for sales voucher {instance.voucher.voucher_number}")
    except Exception as e:
        logger.error(f"Error updating sales voucher totals: {e}")
    finally:
        _signal_processing.discard(signal_key)

# ==================== FINANCIAL RECORD SIGNALS ====================

@receiver(post_save, sender=PurchaseVoucher)
def create_purchase_financial_records(sender, instance, created, **kwargs):
    """Create financial records for purchase vouchers"""
    if not created or instance.status != PurchaseVoucher.Status.COMPLETED:
        return
    
    signal_key = f"purchase_financial_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            # Create daybook entry
            daybook_entry = Daybook.objects.create(
                transaction_type='purchase',
                reference_id=str(instance.id),
                reference_model='PurchaseVoucher',
                description=f"Purchase Voucher {instance.voucher_number} - {instance.vendor.username if instance.vendor else 'Unknown Vendor'}",
                debit_amount=instance.total_amount,  # Purchase is a debit (asset increase)
                credit_amount=Decimal('0.00'),
                balance=instance.total_amount,
                payment_method=instance.payment_method,
                payment_status=instance.payment_status,
                created_by=instance.vendor
            )
            
            # Create cashbook entry if there's any cost (after discount)
            if instance.cost > 0:
                Cashbook.create_entry(
                    entry_type='payment',
                    source_type='purchase',
                    reference_id=instance.voucher_number,
                    reference_model='PurchaseVoucher',
                    description=f"Payment for Purchase Voucher {instance.voucher_number}",
                    amount=instance.cost,
                    payment_method=instance.payment_method,
                    transaction_date=instance.date,
                    is_bank=(instance.payment_method == PaymentMethodChoices.BANK_TRANSFER),
                    recorded_by=instance.vendor,
                    notes=f"Total: {instance.total_amount}, Discount: {instance.discount}"
                )
            
            logger.info(f"Created financial records for purchase voucher {instance.voucher_number}")
            
    except Exception as e:
        logger.error(f"Error creating financial records for purchase voucher {instance.pk}: {e}")
        # Don't raise as it would prevent voucher creation
    finally:
        _signal_processing.discard(signal_key)

@receiver(post_save, sender=SalesVoucher)
def create_sales_financial_records(sender, instance, created, **kwargs):
    """Create financial records for sales vouchers"""
    if not created or instance.status != SalesVoucher.Status.COMPLETED:
        return
    
    signal_key = f"sales_financial_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            # Create daybook entry
            net_amount = instance.total_amount - instance.discount
            
            daybook_entry = Daybook.objects.create(
                transaction_type='sale',
                reference_id=str(instance.id),
                reference_model='SalesVoucher',
                description=f"Sales Voucher {instance.voucher_number} - {instance.customer.name if instance.customer else 'Walk-in Customer'}",
                debit_amount=Decimal('0.00'),
                credit_amount=net_amount,  # Sale is a credit (revenue)
                balance=-net_amount,  # Negative balance for credit
                payment_method=instance.payment_method,
                payment_status=instance.payment_status,
                created_by=None  # Sales don't have a created_by user typically
            )
            
            # Create cashbook entry for received payments
            if instance.paid_amount > 0:
                Cashbook.create_entry(
                    entry_type='receipt',
                    source_type='sale',
                    reference_id=instance.voucher_number,
                    reference_model='SalesVoucher',
                    description=f"Payment received for Sales Voucher {instance.voucher_number}",
                    amount=instance.paid_amount,
                    payment_method=instance.payment_method,
                    transaction_date=instance.date,
                    is_bank=(instance.payment_method == PaymentMethodChoices.BANK_TRANSFER),
                    recorded_by=None,
                    notes=f"Total: {instance.total_amount}, Discount: {instance.discount}, Remaining: {instance.remaining_amount}"
                )
            
            logger.info(f"Created financial records for sales voucher {instance.voucher_number}")
            
    except Exception as e:
        logger.error(f"Error creating financial records for sales voucher {instance.pk}: {e}")
        # Don't raise as it would prevent voucher creation
    finally:
        _signal_processing.discard(signal_key)

# ==================== INVOICE GENERATION ====================

@receiver(post_save, sender=SalesVoucher)
def create_sales_invoice_signal(sender, instance, created, **kwargs):
    """Create sales invoice when sales voucher is completed"""
    if not created or instance.status != SalesVoucher.Status.COMPLETED:
        return
    
    signal_key = f"sales_invoice_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        # Get the first item for invoice (you might want to handle multiple items differently)
        first_item = instance.items.first()
        if not first_item:
            logger.warning(f"No items found for sales voucher {instance.voucher_number}")
            return
        
        with transaction.atomic():
            # Create invoice with data from voucher and first item
            invoice = SalesInvoice.objects.create(
                sales_voucher=instance,
                product_name=first_item.product.name,
                quantity=first_item.quantity,
                unit_price=first_item.price,
                warranty=first_item.warranty,
                customer_name=instance.customer.name if instance.customer else 'Walk-in Customer',
                customer_number=instance.customer.phone if instance.customer else '',
                customer_address=instance.customer.address if instance.customer else '',
                discount_amount=instance.discount,
                paid_amount=instance.paid_amount,
                payment_method=instance.payment_method,
                notes=f"Generated from sales voucher {instance.voucher_number}"
            )
            
            logger.info(f"Created sales invoice {invoice.invoice_number} for voucher {instance.voucher_number}")
            
    except Exception as e:
        logger.error(f"Error creating sales invoice for voucher {instance.pk}: {e}")
        # Don't raise as it would prevent voucher creation
    finally:
        _signal_processing.discard(signal_key)

@receiver(post_save, sender=Repair)
def create_repair_invoice_signal(sender, instance, created, **kwargs):
    """Create repair invoice when repair is completed"""
    if not created or instance.status != 'completed':
        return
    
    signal_key = f"repair_invoice_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            invoice = RepairInvoice.objects.create(
                repair=instance,
                product_name=instance.product_name,
                customer_name=instance.user.username if instance.user else 'Unknown Customer',
                customer_number=getattr(instance.user, 'phone', '') if instance.user else '',
                customer_address=getattr(instance.user, 'address', '') if instance.user else '',
                total_amount=instance.total_amount,
                discount_amount=instance.discount_amount or Decimal('0.00'),
                paid_amount=instance.paid_amount,
                payment_method=instance.payment_method,
                notes=f"Generated from repair order {instance.id}"
            )
            
            logger.info(f"Created repair invoice {invoice.invoice_number} for repair {instance.id}")
            
    except Exception as e:
        logger.error(f"Error creating repair invoice for repair {instance.pk}: {e}")
        # Don't raise as it would prevent repair creation
    finally:
        _signal_processing.discard(signal_key)

# ==================== RETURN MANAGEMENT ====================

@receiver(post_save, sender=Return)
def handle_return_stock_signal(sender, instance, created, **kwargs):
    """Handle stock updates for returns"""
    if not created:
        return
    
    signal_key = f"return_stock_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            # Create stock ledger entry for return (positive quantity)
            StockLedger.create_entry(
                product=instance.product,
                transaction_type='return',
                reference_id=instance.id,
                reference_model='Return',
                quantity=instance.quantity_returned,  # Positive for incoming stock
                unit_cost=instance.product.price,
                created_by=None,
                notes=f"Product return - {instance.reason[:50] if instance.reason else 'No reason provided'}"
            )
            
            # Create financial records for return
            if instance.refund_amount and instance.refund_amount > 0:
                # Daybook entry
                Daybook.objects.create(
                    transaction_type='return',
                    reference_id=str(instance.id),
                    reference_model='Return',
                    description=f"Product return - {instance.product.name}",
                    debit_amount=instance.refund_amount,  # Refund is a debit (cash decrease)
                    credit_amount=Decimal('0.00'),
                    balance=instance.refund_amount,
                    payment_method=PaymentMethodChoices.CASH,  # Default for returns
                    payment_status=PaymentStatusChoices.FULL_PAYMENT,
                    created_by=None
                )
                
                # Cashbook entry
                Cashbook.create_entry(
                    entry_type='payment',
                    source_type='return',
                    reference_id=str(instance.id),
                    reference_model='Return',
                    description=f"Refund for returned product - {instance.product.name}",
                    amount=instance.refund_amount,
                    payment_method=PaymentMethodChoices.CASH,
                    transaction_date=instance.return_date.date(),
                    is_bank=False,
                    recorded_by=None,
                    notes=f"Return quantity: {instance.quantity_returned}"
                )
            
            logger.info(f"Processed return for product {instance.product.name}: +{instance.quantity_returned}")
            
    except Exception as e:
        logger.error(f"Error handling return for return {instance.pk}: {e}")
        # Don't raise as it would prevent return creation
    finally:
        _signal_processing.discard(signal_key)

# ==================== EXPENSE MANAGEMENT ====================

@receiver(post_save, sender=Expense)
def create_expense_records_signal(sender, instance, created, **kwargs):
    """Create financial records for expenses"""
    if not created:
        return
    
    signal_key = f"expense_records_{instance.pk}"
    if signal_key in _signal_processing:
        return
    
    _signal_processing.add(signal_key)
    try:
        with transaction.atomic():
            # Create daybook entry
            Daybook.objects.create(
                transaction_type='expense',
                reference_id=str(instance.id),
                reference_model='Expense',
                description=f"Expense: {instance.get_category_type_display()} - {instance.description[:50] if instance.description else 'No description'}",
                debit_amount=instance.amount,  # Expense is a debit
                credit_amount=Decimal('0.00'),
                balance=instance.amount,
                payment_method=instance.payment_method,
                payment_status=instance.payment_status,
                created_by=None  # Expenses don't have created_by field
            )
            
            # Create cashbook entry if payment is completed
            if instance.payment_status == PaymentStatusChoices.FULL_PAYMENT:
                Cashbook.create_entry(
                    entry_type='payment',
                    source_type='expense',
                    reference_id=str(instance.id),
                    reference_model='Expense',
                    description=f"Expense payment: {instance.get_category_type_display()}",
                    amount=instance.amount,
                    payment_method=instance.payment_method,
                    transaction_date=timezone.now().date(),
                    is_bank=(instance.payment_method == PaymentMethodChoices.BANK_TRANSFER),
                    recorded_by=None,
                    notes=instance.description
                )
            
            logger.info(f"Created financial records for expense {instance.id}: {instance.amount}")
            
    except Exception as e:
        logger.error(f"Error creating expense records for expense {instance.pk}: {e}")
        # Don't raise as it would prevent expense creation
    finally:
        _signal_processing.discard(signal_key)

# ==================== CLEANUP AND MONITORING ====================

@receiver(post_save, sender=Product)
def log_product_changes(sender, instance, created, **kwargs):
    """Log significant product changes for monitoring"""
    if created:
        logger.info(f"New product created: {instance.name} (ID: {instance.id}) with stock: {instance.stock}")
    else:
        # You could add logic here to compare with previous values if needed
        logger.debug(f"Product updated: {instance.name} (ID: {instance.id}) current stock: {instance.stock}")

# Signal to clean up processing flags periodically (optional)
from django.core.management.base import BaseCommand

def cleanup_signal_flags():
    """Clean up any stuck signal processing flags"""
    global _signal_processing
    _signal_processing.clear()
    logger.info("Cleaned up signal processing flags")

# You can call this from a management command or periodic task