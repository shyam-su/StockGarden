# Generated by Django 5.1.5 on 2025-02-09 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='Brand Name')),
                ('image', models.ImageField(blank=True, db_index=True, null=True, upload_to='media/brands_imgs/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Brand',
                'indexes': [models.Index(fields=['name'], name='StockGarden_name_52f7ab_idx')],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Category Name')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Category',
                'indexes': [models.Index(fields=['name'], name='StockGarden_name_4cbcbd_idx')],
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('phone_number', models.CharField(db_index=True, max_length=20)),
                ('logo', models.ImageField(blank=True, upload_to='company/logos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Company',
                'indexes': [models.Index(fields=['name', 'phone_number'], name='StockGarden_name_f91e02_idx')],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='Product Name')),
                ('description', models.TextField(blank=True, db_index=True, max_length=255, null=True)),
                ('price', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, verbose_name='Product Price')),
                ('Imei', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, db_index=True, null=True, upload_to='media/products_imgs/')),
                ('stock', models.IntegerField(blank=True, db_index=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='StockGarden.brand')),
                ('categories', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='StockGarden.category')),
            ],
            options={
                'verbose_name': 'Product',
            },
        ),
        migrations.CreateModel(
            name='Repair',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=100)),
                ('device_model', models.CharField(max_length=100)),
                ('issue_description', models.TextField()),
                ('out_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('in-progress', 'In Progress'), ('completed', 'Completed'), ('pending', 'Pending Pickup')], default='in-progress', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='Customer Name')),
            ],
            options={
                'verbose_name': 'Repair',
            },
        ),
        migrations.CreateModel(
            name='RepairDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('repair_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fixed_description', models.TextField()),
                ('repair_action', models.CharField(choices=[('in', 'In'), ('repairing', 'Repairing'), ('repaired', 'Repaired'), ('returned', 'Returned')], max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('repair_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repair_details', to='StockGarden.repair')),
            ],
            options={
                'verbose_name': 'Repair Detail',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Total_sells', models.IntegerField(blank=True, db_index=True, null=True)),
                ('Total_purchase', models.IntegerField(blank=True, db_index=True, null=True)),
                ('Total_Stock', models.IntegerField(blank=True, db_index=True, null=True)),
                ('Low_Stock', models.IntegerField(blank=True, db_index=True, null=True)),
                ('Empty_Stock', models.IntegerField(blank=True, db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Report',
                'indexes': [models.Index(fields=['Total_sells', 'Total_purchase', 'Total_Stock', 'Low_Stock', 'Empty_Stock'], name='StockGarden_Total_s_745b29_idx')],
            },
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
                ('total', models.IntegerField()),
                ('contact_no', models.CharField(blank=True, max_length=15, null=True)),
                ('expiring_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Sale Date')),
                ('name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='Party Name')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StockGarden.product')),
            ],
            options={
                'verbose_name': 'Seller',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.IntegerField(blank=True, null=True)),
                ('payment_method', models.CharField(choices=[('Cash on Hands', 'Cash on Hands'), ('Khalti', 'Khalti'), ('Esewa', 'Esewa'), ('Bank Transfer', 'Bank Transfer')], db_index=True, max_length=255)),
                ('status', models.CharField(choices=[('Full Payment', 'Full Payment'), ('Pending', 'Pending')], db_index=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sales', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StockGarden.sales')),
            ],
            options={
                'verbose_name': 'Invoice',
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=200, verbose_name='Company Name')),
                ('address', models.CharField(max_length=300)),
                ('contact_no', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='Party Name')),
            ],
            options={
                'verbose_name': 'Vendor',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=300, null=True)),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
                ('total_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(blank=True, default='No Available', null=True, on_delete=django.db.models.deletion.CASCADE, to='StockGarden.product')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StockGarden.vendor')),
            ],
            options={
                'verbose_name': 'Purchase',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='StockGarden.vendor'),
        ),
        migrations.AddIndex(
            model_name='repair',
            index=models.Index(fields=['product_name', 'device_model', 'status'], name='StockGarden_product_f89005_idx'),
        ),
        migrations.AddIndex(
            model_name='repairdetail',
            index=models.Index(fields=['repair_order', 'repair_action'], name='StockGarden_repair__0d18aa_idx'),
        ),
        migrations.AddIndex(
            model_name='sales',
            index=models.Index(fields=['name', 'product', 'price'], name='StockGarden_name_id_1b6e84_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['sales', 'payment_method', 'status'], name='StockGarden_sales_i_0cf642_idx'),
        ),
        migrations.AddIndex(
            model_name='vendor',
            index=models.Index(fields=['name', 'contact_no', 'company_name'], name='StockGarden_name_id_833c38_idx'),
        ),
        migrations.AddIndex(
            model_name='purchase',
            index=models.Index(fields=['product', 'vendor'], name='StockGarden_product_ecd471_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name', 'description', 'price', 'image', 'categories', 'stock', 'brand'], name='StockGarden_name_17b859_idx'),
        ),
    ]
