from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=Purchase)
def create_or_update_product_from_purchase(sender, instance, created, **kwargs):
    product, created = Product.objects.update_or_create(
        vendor=instance.vendor,
        name=instance.product_name,
        defaults={
            "description": instance.description,
            "price": instance.price,
            "warranty": instance.warranty,
            "Imei": instance.Imei,
            "image": instance.image,
            "categories": instance.categories,
            "stock": instance.quantity,
            "brand": instance.brand,
        },
    )

@receiver(post_save, sender=Sales)
def create_or_update_sales_invoice(sender, instance, created, **kwargs):
    SalesInvoice.objects.update_or_create(
        sales=instance,
        defaults={
            "product_name": instance.product.name,
            "warranty": instance.warranty,
            "customer_name": instance.user.full_name if instance.user.full_name else None,
            "customer_number": instance.user.phone if instance.user.phone else None,
            "customer_address": instance.user.address if instance.user.address else None,
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
