# Generated by Django 5.1.5 on 2025-03-31 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockGarden', '0002_alter_sales_user_alter_salesinvoice_customer_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='paid_amount',
            field=models.IntegerField(default=0.0),
        ),
        migrations.AlterField(
            model_name='salesinvoice',
            name='paid_amount',
            field=models.IntegerField(blank=True, default=0.0, null=True),
        ),
    ]
