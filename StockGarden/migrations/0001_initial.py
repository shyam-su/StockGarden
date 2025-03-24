# Generated by Django 5.1.5 on 2025-03-24 10:10

import django.db.models.deletion
import uuid
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
                ('name', models.CharField(db_index=True, max_length=191, unique=True, verbose_name='Brand Name')),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/brands_imgs/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Brand',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, unique=True, verbose_name='Category Name')),
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
                ('name', models.CharField(max_length=191)),
                ('address', models.CharField(max_length=191)),
                ('email', models.EmailField(db_index=True, max_length=191)),
                ('phone_number', models.CharField(db_index=True, max_length=20)),
                ('logo', models.ImageField(blank=True, upload_to='company/logos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Company',
                'indexes': [models.Index(fields=['name'], name='StockGarden_name_d234c5_idx')],
            },
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Expense Category',
                'indexes': [models.Index(fields=['name'], name='StockGarden_name_701d64_idx')],
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('description', models.TextField(blank=True, null=True)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('mobile_payment', 'Mobile Payment'), ('other', 'Other')], db_index=True, default='cash', max_length=20)),
                ('payment_status', models.CharField(choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='StockGarden.expensecategory')),
            ],
            options={
                'verbose_name': 'Expense',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=191, verbose_name='Product Name')),
                ('description', models.TextField(blank=True, max_length=191, null=True)),
                ('price', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, verbose_name='Product Price')),
                ('warranty', models.IntegerField(blank=True, null=True)),
                ('Imei', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/products_imgs/')),
                ('stock', models.IntegerField(blank=True, db_index=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=191, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='StockGarden.brand')),
                ('categories', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='StockGarden.category')),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='user.user')),
            ],
            options={
                'verbose_name': 'Product',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(blank=True, max_length=191, null=True)),
                ('warranty', models.IntegerField(blank=True, null=True)),
                ('condition', models.CharField(choices=[('new', 'New'), ('like_new', 'Like New'), ('good', 'Good'), ('needs_repair', 'Needs Repair')], default='new', max_length=20)),
                ('description', models.TextField(blank=True, max_length=191, null=True)),
                ('Imei', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/products_imgs/')),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchases', to='StockGarden.brand')),
                ('categories', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchased_categories', to='StockGarden.category')),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchases', to='user.user')),
            ],
            options={
                'verbose_name': 'Purchase',
            },
        ),
        migrations.CreateModel(
            name='Repair',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=100)),
                ('device_model', models.CharField(max_length=100)),
                ('issue_description', models.TextField()),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('mobile_payment', 'Mobile Payment'), ('other', 'Other')], db_index=True, default='cash', max_length=20)),
                ('payment_status', models.CharField(choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='Pending', max_length=191)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(choices=[('in-progress', 'In Progress'), ('completed', 'Completed'), ('pending', 'Pending Pickup')], default='in-progress', max_length=20)),
                ('out_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='user.user', verbose_name='Customer Name')),
            ],
            options={
                'verbose_name': 'Repair',
            },
        ),
        migrations.CreateModel(
            name='RepairDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('device_model', models.CharField(max_length=100)),
                ('repair_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('repair_detail_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('issue_description', models.TextField()),
                ('fixed_description', models.TextField()),
                ('repair_action', models.CharField(choices=[('in', 'In'), ('repairing', 'Repairing'), ('repaired', 'Repaired'), ('returned', 'Returned')], max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('repair_order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='details', to='StockGarden.repair')),
            ],
            options={
                'verbose_name': 'Repair Detail',
            },
        ),
        migrations.CreateModel(
            name='RepairInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(default=uuid.uuid4, max_length=36, unique=True)),
                ('product_name', models.CharField(max_length=255)),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_number', models.IntegerField(blank=True, null=True)),
                ('customer_address', models.TextField(blank=True, null=True)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('mobile_payment', 'Mobile Payment'), ('other', 'Other')], db_index=True, default='cash', max_length=20)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_status', models.CharField(choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='pending', max_length=20)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('repair', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repairinvoice', to='StockGarden.repair')),
            ],
            options={
                'verbose_name': 'Repair Invoice',
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
                'indexes': [models.Index(fields=['Total_sells'], name='StockGarden_Total_s_0dc15d_idx')],
            },
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Imei', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('warranty', models.IntegerField(blank=True, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('discount', models.IntegerField(blank=True, default=0, null=True)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('mobile_payment', 'Mobile Payment'), ('other', 'Other')], db_index=True, default='cash', max_length=20)),
                ('payment_status', models.CharField(choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='Pending', max_length=191)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('expiring_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Sale Date')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='StockGarden.product')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='user.user')),
            ],
            options={
                'verbose_name': 'Sells',
            },
        ),
        migrations.CreateModel(
            name='SalesInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(default=uuid.uuid4, max_length=6, unique=True)),
                ('product_name', models.CharField(max_length=255)),
                ('warranty', models.IntegerField(blank=True, null=True)),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_number', models.IntegerField(blank=True, null=True)),
                ('customer_address', models.TextField(blank=True, null=True)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('mobile_payment', 'Mobile Payment'), ('other', 'Other')], db_index=True, default='cash', max_length=20)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_status', models.CharField(choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='pending', max_length=20)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sales', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='salesinvoice', to='StockGarden.sales')),
            ],
            options={
                'verbose_name': 'Sales Invoice',
            },
        ),
        migrations.CreateModel(
            name='Return',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_returned', models.PositiveIntegerField()),
                ('reason', models.TextField(blank=True, null=True)),
                ('return_date', models.DateTimeField(auto_now_add=True)),
                ('refund_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='StockGarden.product')),
                ('invoice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice', to='StockGarden.salesinvoice')),
            ],
            options={
                'verbose_name': 'Product Return',
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='StockGarden_name_42fbbb_idx'),
        ),
        migrations.AddIndex(
            model_name='purchase',
            index=models.Index(fields=['product_name'], name='StockGarden_product_8f02af_idx'),
        ),
        migrations.AddIndex(
            model_name='repair',
            index=models.Index(fields=['product_name'], name='StockGarden_product_d87f79_idx'),
        ),
        migrations.AddIndex(
            model_name='repairdetail',
            index=models.Index(fields=['product_name'], name='StockGarden_product_3edf03_idx'),
        ),
        migrations.AddIndex(
            model_name='repairinvoice',
            index=models.Index(fields=['invoice_number'], name='StockGarden_invoice_0bd60d_idx'),
        ),
        migrations.AddIndex(
            model_name='sales',
            index=models.Index(fields=['user'], name='StockGarden_user_id_96639d_idx'),
        ),
        migrations.AddIndex(
            model_name='salesinvoice',
            index=models.Index(fields=['invoice_number'], name='StockGarden_invoice_9de59a_idx'),
        ),
        migrations.AddIndex(
            model_name='return',
            index=models.Index(fields=['return_date'], name='StockGarden_return__332b87_idx'),
        ),
    ]
