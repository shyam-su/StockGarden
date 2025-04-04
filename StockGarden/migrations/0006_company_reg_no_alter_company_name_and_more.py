# Generated by Django 5.1.5 on 2025-04-04 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockGarden', '0005_purchase_payment_method_purchase_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='reg_no',
            field=models.CharField(db_index=True, default=None, max_length=20, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=191, unique=True, verbose_name='Company Name'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='pending', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='Pending', max_length=191, null=True),
        ),
        migrations.AlterField(
            model_name='repair',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='Pending', max_length=191, null=True),
        ),
        migrations.AlterField(
            model_name='repairinvoice',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='pending', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='sales',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='Pending', max_length=191, null=True),
        ),
        migrations.AlterField(
            model_name='salesinvoice',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('Full Payment', 'Full Payment'), ('Partial Payment', 'Partial Payment'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], db_index=True, default='pending', max_length=20, null=True),
        ),
    ]
