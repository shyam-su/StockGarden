# Generated by Django 5.1.5 on 2025-03-22 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockGarden', '0003_remove_repair_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repair',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='repairdetail',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
