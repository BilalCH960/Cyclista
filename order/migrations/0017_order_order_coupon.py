# Generated by Django 5.0.1 on 2024-05-05 12:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_coupon'),
        ('order', '0016_alter_payment_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cart.coupon'),
        ),
    ]
