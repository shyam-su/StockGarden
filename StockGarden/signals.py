from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=Purchase)
def create_product_from_purchase(sender, instance, created, **kwargs):
    if created:
        Product.objects.create(
            vendor=instance.vendor,
            name=instance.product_name,
            description=instance.description,
            price=instance.price,
            Imei=instance.Imei,
            image=instance.image,
            categories=instance.categories,
            stock=instance.quantity,
            brand=instance.brand
        )

@receiver(post_save, sender=Sales)
def generate_sells_invoice(sender, instance, created, **kwargs):
    if created:
        SalesInvoice.objects.create(
            sales=instance, 
            product_name=instance.product.name, 
            customer_name=instance.user.full_name,
            customer_number=instance.user.phone if instance.user.phone else None,
            customer_address=instance.user.address if instance.user.address else None,
            payment_method=instance.payment_method,
            total_amount=instance.price * instance.quantity,
            discount_amount=instance.discount,
            payment_status=instance.payment_status,
            due_date=instance.due_date,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )
        
@receiver(post_save, sender=Repair)
def create_repairdetail_from_repair(sender, instance, created, **kwargs):
    if created:
        RepairDetail.objects.create(
            repair_order=instance,
            product_name=instance.product_name,
            device_model=instance.device_model,
            fixed_description=instance.issue_description,
            created_at=instance.created_at
        )
        
@receiver(post_save, sender=Repair)
def generate_repair_invoice(sender, instance, created, **kwargs):
    if created:
        RepairInvoice.objects.create(
            repair=instance, 
            product_name=instance.product_name, 
            customer_name=instance.user.full_name,
            customer_number=instance.user.phone if instance.user.phone else None,
            customer_address=instance.user.address if instance.user.address else None,
            payment_method=instance.payment_method,
            total_amount=instance.total_amount,
            discount_amount=instance.discount_amount,
            payment_status=instance.payment_status,
            created_at=instance.created_at,
        )