# Generated by Django 5.1.5 on 2025-03-17 06:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockGarden', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media/brands_imgs/'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(db_index=True, max_length=191, verbose_name='Brand Name'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(db_index=True, max_length=191),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_method',
            field=models.CharField(choices=[('Cash on Hands', 'Cash on Hands'), ('Khalti', 'Khalti'), ('Esewa', 'Esewa'), ('Bank Transfer', 'Bank Transfer')], db_index=True, max_length=191),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('Full Payment', 'Full Payment'), ('Pending', 'Pending')], db_index=True, max_length=191),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=191, verbose_name='Product Name'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='product',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='StockGarden.product'),
        ),
        migrations.AlterField(
            model_name='sales',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
