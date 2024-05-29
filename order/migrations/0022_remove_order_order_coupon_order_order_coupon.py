# Generated by Django 5.0.1 on 2024-05-25 12:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0010_coupon_max_discount_amount'),
        ('order', '0021_alter_orderitem_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_coupon',
        ),
        migrations.AddField(
            model_name='order',
            name='order_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cart.coupon'),
        ),
    ]