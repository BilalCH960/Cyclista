# Generated by Django 5.0.1 on 2024-03-26 05:17

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
        ('ad_product', '0019_alter_productvariant_color'),
        ('order', '0005_alter_cartorder_product_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartorderitems',
            name='order',
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_number', models.AutoField(primary_key=True, serialize=False)),
                ('order_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('order_subtotal', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('order_shipping', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('order_update_time', models.DateTimeField(auto_now=True)),
                ('billing_address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='billing_address', to='account.address')),
                ('shipping_address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_address', to='account.address')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(choices=[('COD', 'Cash On Delivery')], max_length=100)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('FAILED', 'Failed'), ('SUCCESS', 'Success')], max_length=20)),
                ('payment_id', models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('payment_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_item_id', models.CharField(default='#0000000', max_length=120)),
                ('order_status', models.CharField(choices=[('PLACED', 'Order Placed'), ('PROCESSING', 'Order Processing'), ('SHIPPED', 'Order Shipped'), ('OUT FOR DELIVERY', 'Out For Delivery'), ('DELIVERED', 'Order Delivered'), ('CANCELLED', 'Order Cancelled'), ('RETURNED', 'Order Returned')], default='PLACED', max_length=20)),
                ('quantity', models.IntegerField(default=1)),
                ('product_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True)),
                ('ordered_time', models.DateTimeField(auto_now_add=True)),
                ('order_updated_time', models.DateTimeField(auto_now=True)),
                ('cancel_reason', models.TextField(blank=True, max_length=200, null=True)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='order.order')),
                ('order_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ad_product.productvariant')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('payment_details', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.payment')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='payment_details',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.payment'),
        ),
        migrations.DeleteModel(
            name='CartOrder',
        ),
        migrations.DeleteModel(
            name='CartOrderItems',
        ),
    ]