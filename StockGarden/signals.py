from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import *
from django.db import transaction
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Purchase)
def adjust_stock_on_purchase_update(sender, instance, **kwargs):
    """Adjust Product stock before saving a Purchase (create or update)."""
    if not instance.product_name:
        logger.warning(f"Purchase {instance.pk or 'new'} has no product_name, skipping stock adjustment.")
        return

    if instance.quantity < 0:
        logger.error(f"Purchase {instance.pk or 'new'} has negative quantity: {instance.quantity}")
        raise ValueError("Purchase quantity cannot be negative.")

    try:
        with transaction.atomic():
            # Lock the product to prevent race conditions
            existing_product = Product.objects.select_for_update().filter(
                vendor=instance.vendor,
                name=instance.product_name,
                brand=instance.brand
            ).first()

            if instance.pk:  # Updating an existing purchase
                try:
                    old_purchase = Purchase.objects.get(pk=instance.pk)
                    if old_purchase.quantity != instance.quantity:
                        quantity_diff = instance.quantity - old_purchase.quantity
                        if existing_product:
                            existing_product.stock = (existing_product.stock or 0) + quantity_diff
                            existing_product.save()
                            logger.info(f"Adjusted Product {existing_product.pk} stock by {quantity_diff} to {existing_product.stock} for Purchase {instance.pk}")
                        else:
                            logger.warning(f"No existing Product found for Purchase {instance.pk} during update, stock not adjusted.")
                    else:
                        logger.info(f"No quantity change for Purchase {instance.pk}, skipping stock adjustment.")
                except Purchase.DoesNotExist:
                    logger.error(f"Old Purchase {instance.pk} not found during update.")
                    raise ValueError("Cannot update purchase: Original purchase not found.")
            else:  # Creating a new purchase
                if existing_product:
                    existing_product.stock = (existing_product.stock or 0) + instance.quantity
                    existing_product.save()
                    logger.info(f"Incremented Product {existing_product.pk} stock by {instance.quantity} to {existing_product.stock} for new Purchase")
                # Stock for new product will be set in post_save
    except Exception as e:
        logger.error(f"Error in adjust_stock_on_purchase_update for Purchase {instance.pk or 'new'}: {e}", exc_info=True)
        raise

@receiver(post_save, sender=Purchase)
def create_or_update_product_from_purchase(sender, instance, created, **kwargs):
    """Create or update a Product based on a Purchase, handling non-stock fields and new product creation."""
    if not instance.product_name:
        logger.warning(f"Purchase {instance.pk} has no product_name, skipping product creation/update.")
        return

    try:
        with transaction.atomic():
            # Lock the product to prevent race conditions
            existing_product = Product.objects.select_for_update().filter(
                vendor=instance.vendor,
                name=instance.product_name,
                brand=instance.brand
            ).first()

            if existing_product:
                # Update non-stock fields
                existing_product.description = instance.description if instance.description is not None else existing_product.description
                existing_product.price = instance.price if instance.price is not None else existing_product.price
                existing_product.warranty = instance.warranty if instance.warranty is not None else existing_product.warranty
                existing_product.Imei = instance.Imei if instance.Imei is not None else existing_product.Imei
                existing_product.image = instance.image if instance.image is not None else existing_product.image
                existing_product.categories = instance.categories if instance.categories is not None else existing_product.categories
                existing_product.brand = instance.brand if instance.brand is not None else existing_product.brand
                existing_product.save()
                logger.info(f"Updated Product {existing_product.pk} non-stock fields for Purchase {instance.pk}")
            elif created:
                # Create new product with stock equal to purchase quantity
                new_product = Product.objects.create(
                    vendor=instance.vendor,
                    name=instance.product_name,
                    description=instance.description,
                    price=instance.price,
                    warranty=instance.warranty,
                    Imei=instance.Imei,
                    image=instance.image,
                    categories=instance.categories,
                    stock=instance.quantity,  # Set stock to purchase quantity
                    brand=instance.brand,
                )
                logger.info(f"Created new Product {new_product.pk} for Purchase {instance.pk} with stock {new_product.stock}")
    except Exception as e:
        logger.error(f"Error in create_or_update_product_from_purchase for Purchase {instance.pk}: {e}", exc_info=True)
        raise

@receiver(post_delete, sender=Purchase)
def remove_stock_on_purchase_delete(sender, instance, **kwargs):
    """Remove stock from Product when a Purchase is deleted."""
    if not instance.product_name:
        logger.warning(f"Deleted Purchase {instance.pk} has no product_name, skipping stock adjustment.")
        return

    try:
        with transaction.atomic():
            # Lock the product to prevent race conditions
            product = Product.objects.select_for_update().filter(
                vendor=instance.vendor,
                name=instance.product_name,
                brand=instance.brand
            ).first()

            if product:
                product.stock = (product.stock or 0) - instance.quantity
                product.save()
                logger.info(f"Reduced Product {product.pk} stock by {instance.quantity} to {product.stock} after Purchase {instance.pk} deletion")
            else:
                logger.warning(f"No Product found for deleted Purchase {instance.pk}, no stock adjustment made.")
    except Exception as e:
        logger.error(f"Error in remove_stock_on_purchase_delete for Purchase {instance.pk}: {e}", exc_info=True)
        raise

@receiver(pre_save, sender=Sales)
def adjust_stock_on_sales_update(sender, instance, **kwargs):
    if not instance.product or instance.quantity is None:
        logger.warning(f"Sales {instance.pk or 'new'} missing product or quantity.")
        return

    try:
        with transaction.atomic():
            # Lock the product row for safe concurrent access
            product = Product.objects.select_for_update().get(pk=instance.product.pk)

            # If updating an existing sale (instance.pk is not None)
            if instance.pk:
                try:
                    old_sale = Sales.objects.get(pk=instance.pk)
                except Sales.DoesNotExist:
                    logger.error(f"Sales record with ID {instance.pk} not found for update.")
                    raise ValueError("Original sale record not found.")

                old_quantity = old_sale.quantity
                new_quantity = instance.quantity
                quantity_diff = old_quantity - new_quantity  # Positive if reducing sale, negative if increasing sale

                # Check for sufficient stock when increasing quantity
                if quantity_diff < 0 and product.stock < abs(quantity_diff):
                    raise ValueError("Insufficient stock to increase sale quantity.")

                # Apply the stock adjustment
                product.stock += quantity_diff
                logger.info(f"Adjusted stock by {quantity_diff}, new stock: {product.stock}")

            else:
                # If this is a new sale, check if there is enough stock
                if product.stock < instance.quantity:
                    raise ValueError("Insufficient stock to create sale.")

                # Reduce stock for the new sale
                product.stock -= instance.quantity
                logger.info(f"Created new sale, reduced stock by {instance.quantity}, new stock: {product.stock}")

            # Handle negative stock
            if product.stock < 0:
                # If stock goes negative, raise an error
                raise ValueError(f"Stock for {product.name} went negative, which is invalid.")

            # Save the product after adjusting the stock
            product.save()

    except Exception as e:
        # Log and re-raise the error if something goes wrong
        logger.error(f"Error adjusting stock for Sales {instance.pk or 'new'}: {e}", exc_info=True)
        raise

@receiver(post_delete, sender=Sales)
def restore_stock_on_sales_delete(sender, instance, **kwargs):
    """Restore Product stock when a Sales instance is deleted."""
    if not instance.product or instance.quantity is None:
        logger.warning(f"Deleted Sales {instance.pk} missing product or quantity, skipping stock adjustment.")
        return

    try:
        with transaction.atomic():
            # Lock the product to prevent race conditions
            product = Product.objects.select_for_update().get(pk=instance.product.pk)
            product.stock += instance.quantity
            product.save()
            logger.info(f"Restored Product {product.pk} stock by {instance.quantity} to {product.stock} after Sales {instance.pk} deletion")
    except Exception as e:
        logger.error(f"Error in restore_stock_on_sales_delete for Sales {instance.pk}: {e}", exc_info=True)
        raise

@receiver(pre_save, sender=Return)
def adjust_stock_on_return_update(sender, instance, **kwargs):
    if not instance.product or instance.quantity_returned is None:
        logger.warning(f"Return {instance.pk or 'new'} missing product or quantity.")
        return
    try:
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=instance.product.pk)
            if instance.pk:  # Updating an existing return
                try:
                    old_return = Return.objects.get(pk=instance.pk)
                    old_quantity = old_return.quantity_returned
                    new_quantity = instance.quantity_returned
                    quantity_diff = new_quantity - old_quantity
                    product.stock += quantity_diff
                    logger.info(f"Adjusted stock by {quantity_diff} for Return {instance.pk}, new stock: {product.stock}")
                except Return.DoesNotExist:
                    logger.error(f"Return record with ID {instance.pk} not found for update.")
                    return
            else:  # Creating a new return
                product.stock += instance.quantity_returned
                logger.info(f"Created new return, increased stock by {instance.quantity_returned}, new stock: {product.stock}")
            product.save()
    except Exception as e:
        logger.error(f"Error adjusting stock for Return {instance.pk or 'new'}: {e}", exc_info=True)
        raise

@receiver(post_delete, sender=Return)
def remove_stock_on_return_delete(sender, instance, **kwargs):
    if not instance.product or instance.quantity_returned is None:
        logger.warning(f"Deleted Return {instance.pk} missing product or quantity, skipping stock adjustment.")
        return
    try:
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=instance.product.pk)
            product.stock -= instance.quantity_returned
            product.save()
            logger.info(f"Reduced Product {product.pk} stock by {instance.quantity_returned} to {product.stock} after Return {instance.pk} deletion")
    except Exception as e:
        logger.error(f"Error in remove_stock_on_return_delete for Return {instance.pk}: {e}", exc_info=True)
        raise



@receiver(post_save, sender=Sales)
def create_or_update_sales_invoice(sender, instance, created, **kwargs):
    SalesInvoice.objects.update_or_create(
        sales=instance,
        defaults={
            "product_name": instance.product.name,
            "warranty": instance.warranty,
            "customer_name": getattr(instance.user, "full_name", None),
            "customer_number": getattr(instance.user, "phone", None),
            "customer_address": getattr(instance.user, "address", None),
            "payment_method": instance.payment_method,
            "quantity": instance.quantity,
            "subtotal": instance.total_amount - instance.discount,  # Ensure correct subtotal
            "discount_amount": instance.discount,
            "paid_amount": instance.paid_amount,
            "remaining_amount": instance.remaining_amount,
            "payment_status": instance.payment_status,
            "due_date": instance.due_date,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        },
    )

@receiver(post_save, sender=Repair)
def create_or_update_repair_details_and_invoice(sender, instance, created, **kwargs):
    RepairDetail.objects.update_or_create(
        repair_order=instance,
        defaults={
            "product_name": instance.product_name,
            "device_model": instance.device_model,
            "repair_cost": instance.total_amount,
            "issue_description": instance.issue_description,
            "created_at": instance.created_at,
        },
    )

    RepairInvoice.objects.update_or_create(
        repair=instance,
        defaults={
            "product_name": instance.product_name,
            "customer_name": instance.user.full_name,
            "customer_number": instance.user.phone if instance.user.phone else None,
            "customer_address": instance.user.address if instance.user.address else None,
            "payment_method": instance.payment_method,
            "total_amount": instance.total_amount,
            "discount_amount": instance.discount_amount,
            "paid_amount": instance.paid_amount,
            "remaining_amount": instance.remaining_amount,
            "payment_status": instance.payment_status,
            "created_at": instance.created_at,
        },
    )


@receiver(post_save, sender=Sales)
def create_sales_daybook_entry(sender, instance, created, **kwargs):
    if created:
        Daybook.objects.create(
            transaction_type='sale',
            reference_id=instance.id,
            reference_model='Sales',
            description=f"Sale of {instance.product.name} (Qty: {instance.quantity})",
            debit_amount=instance.total_amount,
            credit_amount=0,
            balance=instance.total_amount,
            payment_method=instance.payment_method,
            payment_status=instance.payment_status,
            created_by=instance.user
        )

@receiver(post_save, sender=Purchase)
def create_purchase_daybook_entry(sender, instance, created, **kwargs):
    if created:
        Daybook.objects.create(
            transaction_type='purchase',
            reference_id=instance.id,
            reference_model='Purchase',
            description=f"Purchase of {instance.product_name} from {instance.vendor.full_name}",
            debit_amount=0,
            credit_amount=instance.total_price,
            balance=-instance.total_price,
            payment_method=instance.payment_method,
            payment_status=instance.payment_status,
            created_by=instance.vendor
        )

@receiver(post_save, sender=Expense)
def create_expense_daybook_entry(sender, instance, created, **kwargs):
    if created:
        Daybook.objects.create(
            transaction_type='expense',
            reference_id=instance.id,
            reference_model='Expense',
            description=f"Expense: {instance.get_category_type_display()}",
            debit_amount=0,
            credit_amount=instance.amount,
            balance=-instance.amount,
            payment_method=instance.payment_method,
            payment_status=instance.payment_status,
            created_by=None  # Can be set to the user who created the expense if available
        )

@receiver(post_save, sender=Repair)
def create_repair_daybook_entry(sender, instance, created, **kwargs):
    if created and instance.total_amount:
        Daybook.objects.create(
            transaction_type='repair',
            reference_id=instance.id,
            reference_model='Repair',
            description=f"Repair service for {instance.device_model}",
            debit_amount=instance.total_amount,
            credit_amount=0,
            balance=instance.total_amount,
            payment_method=instance.payment_method,
            payment_status=instance.payment_status,
            created_by=instance.user
        )

@receiver(post_save, sender=Return)
def create_return_daybook_entry(sender, instance, created, **kwargs):
    if created:
        Daybook.objects.create(
            transaction_type='return',
            reference_id=instance.id,
            reference_model='Return',
            description=f"Return of {instance.product.name} (Qty: {instance.quantity_returned})",
            debit_amount=0,
            credit_amount=instance.refund_amount,
            balance=-instance.refund_amount,
            payment_method=None,
            payment_status='Full Payment',
            created_by=None
        )

@receiver(post_save, sender=Sales)
def create_sales_cashbook_entry(sender, instance, created, **kwargs):
    if created and instance.payment_method in ['cash', 'bank_transfer', 'mobile_payment']:
        Cashbook.objects.create(
            entry_type='receipt',
            source_type='sale',
            reference_id=instance.id,
            reference_model='Sales',
            description=f"Payment for sale of {instance.product.name}",
            amount=instance.paid_amount,
            payment_method=instance.payment_method,
            is_bank=instance.payment_method != 'cash',
            transaction_date=instance.created_at.date(),
            recorded_by=instance.user
        )

@receiver(post_save, sender=Purchase)
def create_purchase_cashbook_entry(sender, instance, created, **kwargs):
    if created and instance.payment_method in ['cash', 'bank_transfer', 'mobile_payment'] and instance.paid_amount > 0:
        Cashbook.objects.create(
            entry_type='payment',
            source_type='purchase',
            reference_id=instance.id,
            reference_model='Purchase',
            description=f"Payment for purchase of {instance.product_name}",
            amount=instance.paid_amount,
            payment_method=instance.payment_method,
            is_bank=instance.payment_method != 'cash',
            transaction_date=instance.created_at.date(),
            recorded_by=instance.vendor
        )

@receiver(post_save, sender=Expense)
def create_expense_cashbook_entry(sender, instance, created, **kwargs):
    if created and instance.payment_method in ['cash', 'bank_transfer', 'mobile_payment']:
        Cashbook.objects.create(
            entry_type='payment',
            source_type='expense',
            reference_id=instance.id,
            reference_model='Expense',
            description=f"Payment for expense: {instance.get_category_type_display()}",
            amount=instance.amount,
            payment_method=instance.payment_method,
            is_bank=instance.payment_method != 'cash',
            transaction_date=instance.created_at.date(),
            recorded_by=None  # Can be set to the user who created the expense
        )

@receiver(post_save, sender=Repair)
def create_repair_cashbook_entry(sender, instance, created, **kwargs):
    if created and instance.payment_method in ['cash', 'bank_transfer', 'mobile_payment'] and instance.paid_amount > 0:
        Cashbook.objects.create(
            entry_type='receipt',
            source_type='repair',
            reference_id=instance.id,
            reference_model='Repair',
            description=f"Payment for repair of {instance.device_model}",
            amount=instance.paid_amount,
            payment_method=instance.payment_method,
            is_bank=instance.payment_method != 'cash',
            transaction_date=instance.created_at.date(),
            recorded_by=instance.user
        )

@receiver(post_save, sender=Return)
def create_return_cashbook_entry(sender, instance, created, **kwargs):
    if created and instance.refund_amount > 0:
        # Assuming returns are always cash payments (adjust if you have other methods)
        Cashbook.objects.create(
            entry_type='payment',
            source_type='return',
            reference_id=instance.id,
            reference_model='Return',
            description=f"Refund for return of {instance.product.name}",
            amount=instance.refund_amount,
            payment_method='cash',
            is_bank=False,
            transaction_date=instance.return_date.date(),
            recorded_by=None  # Can be set to the user who processed the return
        )
        
def create_stock_ledger_entry(instance, transaction_type, quantity, unit_cost, reference_model):
    """
    Creates a stock ledger entry for inventory tracking
    Handles both Purchase (which uses product_name) and Sales/Return (which use product FK)
    """
    try:
        with transaction.atomic():
            # Determine the product based on the model type
            if reference_model == 'Purchase':
                # For Purchase model, we need to find the product by name
                try:
                    product = Product.objects.get(
                        name=instance.product_name,
                        brand=instance.brand,
                        vendor=instance.vendor
                    )
                except Product.DoesNotExist:
                    logger.error(f"Product {instance.product_name} not found for purchase {instance.id}")
                    return
            else:
                # For Sales and Return models, we can use the product FK directly
                product = instance.product
            
            # Create the ledger entry
            StockLedger.objects.create(
                product=product,
                transaction_type=transaction_type,
                reference_id=instance.id,
                reference_model=reference_model,
                quantity=quantity,
                unit_cost=unit_cost,
                created_by=getattr(instance, 'user', None) or getattr(instance, 'vendor', None)
            )
    except Exception as e:
        logger.error(f"Error creating stock ledger entry: {e}", exc_info=True)
        raise

@receiver(post_save, sender=Purchase)
def create_purchase_ledger_entry(sender, instance, created, **kwargs):
    """
    Creates ledger entry when a new purchase is made
    Only triggers for new purchases (created=True)
    """
    if created:
        create_stock_ledger_entry(
            instance=instance,
            transaction_type='purchase',
            quantity=instance.quantity,
            unit_cost=instance.price,
            reference_model='Purchase'
        )

@receiver(post_save, sender=Sales)
def create_sale_ledger_entry(sender, instance, created, **kwargs):
    """
    Creates ledger entry when a new sale is made
    Only triggers for new sales (created=True)
    Uses negative quantity to indicate stock reduction
    """
    if created:
        create_stock_ledger_entry(
            instance=instance,
            transaction_type='sale',
            quantity=-instance.quantity,  # Negative for outgoing stock
            unit_cost=instance.price,
            reference_model='Sales'
        )

@receiver(post_save, sender=Return)
def create_return_ledger_entry(sender, instance, created, **kwargs):
    """
    Creates ledger entry when a product is returned
    Only triggers for new returns (created=True)
    """
    if created:
        create_stock_ledger_entry(
            instance=instance,
            transaction_type='return',
            quantity=instance.quantity_returned,
            unit_cost=instance.product.price,
            reference_model='Return'
        )

@receiver(post_delete, sender=Purchase)
def reverse_purchase_ledger_entry(sender, instance, **kwargs):
    """
    Creates reversal entry when a purchase is deleted
    Uses negative quantity to reverse the original entry
    """
    create_stock_ledger_entry(
        instance=instance,
        transaction_type='purchase',
        quantity=-instance.quantity,  # Reverse the original entry
        unit_cost=instance.price,
        reference_model='Purchase'
    )

@receiver(post_delete, sender=Sales)
def reverse_sale_ledger_entry(sender, instance, **kwargs):
    """
    Creates reversal entry when a sale is deleted
    Uses positive quantity to reverse the original negative entry
    """
    create_stock_ledger_entry(
        instance=instance,
        transaction_type='sale',
        quantity=instance.quantity,  # Reverse the original entry
        unit_cost=instance.price,
        reference_model='Sales'
    )

@receiver(post_delete, sender=Return)
def reverse_return_ledger_entry(sender, instance, **kwargs):
    """
    Creates reversal entry when a return is deleted
    Uses negative quantity to reverse the original entry
    """
    create_stock_ledger_entry(
        instance=instance,
        transaction_type='return',
        quantity=-instance.quantity_returned,  # Reverse the original entry
        unit_cost=instance.product.price,
        reference_model='Return'
    )
    
@receiver(pre_save, sender=Sales)
def validate_sales_transaction(sender, instance, **kwargs):
    """Validate sales data before saving"""
    try:
        if instance.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")
        if instance.price <= 0:
            raise ValidationError("Price must be greater than zero")
    except Exception as e:
        logger.error(f"Sales validation error: {str(e)}")
        raise ValidationError(str(e))

@receiver(post_save, sender=Sales)
def create_sales_ledger_entries(sender, instance, created, **kwargs):
    """Create ledger entries when a sale is made"""
    try:
        if created or instance.total_amount_changed():
            # Get or create relevant accounts
            sales_account, _ = Account.objects.get_or_create(
                code='4000',
                defaults={
                    'name': 'Sales Revenue',
                    'account_type': AccountType.INCOME
                }
            )
            
            cash_account, _ = Account.objects.get_or_create(
                code='1000',
                defaults={
                    'name': 'Cash',
                    'account_type': AccountType.ASSET
                }
            )
            
            accounts_receivable, _ = Account.objects.get_or_create(
                code='1100',
                defaults={
                    'name': 'Accounts Receivable',
                    'account_type': AccountType.ASSET
                }
            )
            
            # Create ledger entries
            if instance.payment_method == PaymentMethodChoices.CASH:
                LedgerEntry.objects.create(
                    date=instance.created_at,
                    account=cash_account,
                    debit_amount=instance.total_amount,
                    description=f"Cash sale of {instance.product.name}",
                    transaction_type='sale',
                    transaction_id=instance.id,
                    created_by=instance.user
                )
            else:
                LedgerEntry.objects.create(
                    date=instance.created_at,
                    account=accounts_receivable,
                    debit_amount=instance.total_amount,
                    description=f"Credit sale of {instance.product.name}",
                    transaction_type='sale',
                    transaction_id=instance.id,
                    created_by=instance.user
                )
            
            LedgerEntry.objects.create(
                date=instance.created_at,
                account=sales_account,
                credit_amount=instance.total_amount,
                description=f"Sale of {instance.product.name}",
                transaction_type='sale',
                transaction_id=instance.id,
                created_by=instance.user
            )
    except Exception as e:
        logger.error(f"Error creating ledger entries for sale {instance.id}: {str(e)}")
        # Optionally, you could send an alert to admins here
        
        
@receiver(post_save, sender=Purchase)
def create_purchase_ledger_entries(sender, instance, created, **kwargs):
    """Create ledger entries when a purchase is made"""
    try:
        if created or instance.total_price_changed():
            # Get or create relevant accounts
            inventory_account, _ = Account.objects.get_or_create(
                code='1200',
                defaults={
                    'name': 'Inventory',
                    'account_type': AccountType.ASSET
                }
            )
            
            accounts_payable, _ = Account.objects.get_or_create(
                code='2000',
                defaults={
                    'name': 'Accounts Payable',
                    'account_type': AccountType.LIABILITY
                }
            )
            
            cash_account, _ = Account.objects.get_or_create(
                code='1000',
                defaults={
                    'name': 'Cash',
                    'account_type': AccountType.ASSET
                }
            )
            
            # Create ledger entries
            if instance.payment_method == PaymentMethodChoices.CASH:
                LedgerEntry.objects.create(
                    date=instance.created_at,
                    account=inventory_account,
                    debit_amount=instance.total_price,
                    description=f"Cash purchase of {instance.product_name}",
                    transaction_type='purchase',
                    transaction_id=instance.id,
                    created_by=instance.vendor
                )
                
                LedgerEntry.objects.create(
                    date=instance.created_at,
                    account=cash_account,
                    credit_amount=instance.total_price,
                    description=f"Cash payment for {instance.product_name}",
                    transaction_type='purchase',
                    transaction_id=instance.id,
                    created_by=instance.vendor
                )
            else:
                LedgerEntry.objects.create(
                    date=instance.created_at,
                    account=inventory_account,
                    debit_amount=instance.total_price,
                    description=f"Credit purchase of {instance.product_name}",
                    transaction_type='purchase',
                    transaction_id=instance.id,
                    created_by=instance.vendor
                )
                
                LedgerEntry.objects.create(
                    date=instance.created_at,
                    account=accounts_payable,
                    credit_amount=instance.total_price,
                    description=f"Credit purchase of {instance.product_name}",
                    transaction_type='purchase',
                    transaction_id=instance.id,
                    created_by=instance.vendor
                )
    except Exception as e:
        logger.error(f"Error creating ledger entries for purchase {instance.id}: {str(e)}")