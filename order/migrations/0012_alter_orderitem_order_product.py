# Generated by Django 5.0.1 on 2024-04-25 09:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad_product', '0019_alter_productvariant_color'),
        ('order', '0011_alter_orderitem_order_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ad_product.productvariant'),
        ),
    ]