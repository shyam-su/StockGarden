# Generated by Django 5.1.5 on 2025-03-23 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockGarden', '0002_repairdetail_repair_detail_cost_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
