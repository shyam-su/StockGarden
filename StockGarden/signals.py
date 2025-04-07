from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import *
from django.db import transaction


@receiver(post_save, sender=Purchase)
def create_or_update_product_from_purchase(sender, instance, created, **kwargs):
    if not instance.product_name: 
        return

    with transaction.atomic(): 
        existing_product = Product.objects.filter(
            vendor=instance.vendor,
            name=instance.product_name
        ).first()

        if existing_product:
            if created:
                new_stock = (existing_product.stock or 0) + instance.quantity
            else:
                old_purchase = Purchase.objects.get(pk=instance.pk)
                if old_purchase.quantity != instance.quantity:
                    stock_diff = instance.quantity - old_purchase.quantity
                    new_stock = (existing_product.stock or 0) + stock_diff
                else:
                    new_stock = existing_product.stock

            Product.objects.filter(pk=existing_product.pk).update(
                description=instance.description or existing_product.description,
                price=instance.price or existing_product.price,
                warranty=instance.warranty or existing_product.warranty,
                Imei=instance.Imei or existing_product.Imei,
                image=instance.image or existing_product.image,
                categories=instance.categories or existing_product.categories,
                brand=instance.brand or existing_product.brand,
                stock=new_stock 
            )
        else:
            Product.objects.create(
                vendor=instance.vendor,
                name=instance.product_name,
                description=instance.description,
                price=instance.price,
                warranty=instance.warranty,
                Imei=instance.Imei,
                image=instance.image,
                categories=instance.categories,
                stock=instance.quantity,
                brand=instance.brand,
            )


@receiver(pre_save, sender=Sales)
def adjust_stock_on_sales_update(sender, instance, **kwargs):
    """Adjust stock before saving a Sales instance (create or update)."""
    with transaction.atomic():
        if instance.pk:  # Updating an existing sale
            old_sale = Sales.objects.get(pk=instance.pk)
            if old_sale.quantity != instance.quantity:
                stock_diff = old_sale.quantity - instance.quantity  # Positive if qty reduced, negative if increased
                if instance.product.stock + stock_diff >= 0:
                    instance.product.stock += stock_diff
                    instance.product.save()
                else:
                    raise ValueError("Insufficient stock to update this sale.")
        else:  # Creating a new sale
            if instance.product.stock < instance.quantity:
                raise ValueError("Insufficient stock for this sale.")
            instance.product.stock -= instance.quantity
            instance.product.save()

@receiver(post_delete, sender=Sales)
def restore_stock_on_sales_delete(sender, instance, **kwargs):
    """Restore stock when a Sales instance is deleted."""
    with transaction.atomic():
        instance.product.stock += instance.quantity
        instance.product.save()

@receiver(pre_save, sender=Return)
def adjust_stock_on_return_update(sender, instance, **kwargs):
    if not instance.product or instance.quantity_returned is None:
        return

    with transaction.atomic():
        product = Product.objects.select_for_update().get(pk=instance.product.pk)
        
        if instance.pk:  # Updating an existing return
            try:
                old_return = Return.objects.get(pk=instance.pk)
                if old_return.quantity_returned != instance.quantity_returned:
                    quantity_diff = instance.quantity_returned - old_return.quantity_returned
                    if product.stock + quantity_diff < 0:
                        raise ValueError("Stock cannot go negative after update.")
                    product.stock += quantity_diff
                    product.save()
            except Return.DoesNotExist:
                raise ValueError("Original return record not found")
        else:  # Creating a new return
            if product.stock + instance.quantity_returned < 0:  # Optional: Add validation
                raise ValueError("Stock cannot go negative after new return.")
            product.stock += instance.quantity_returned
            product.save()
            

@receiver(post_delete, sender=Return)
def remove_stock_on_return_delete(sender, instance, **kwargs):
    """Remove stock when a Return instance is deleted."""
    with transaction.atomic():
        if instance.product.stock >= instance.quantity_returned:
            instance.product.stock -= instance.quantity_returned
            instance.product.save()
        else:
            raise ValueError("Cannot delete return: insufficient stock to subtract.")
        



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
