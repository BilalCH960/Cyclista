# Generated by Django 5.0.1 on 2024-02-03 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_product_mfd_alter_product_stock_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='mfd',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]