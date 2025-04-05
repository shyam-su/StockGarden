from django.db.models.signals import post_save
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
