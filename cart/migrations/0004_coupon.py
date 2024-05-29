# Generated by Django 5.0.1 on 2024-05-05 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_remove_cartorderitems_order_cart_cart_item_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('valid_from', models.DateTimeField(auto_now_add=True)),
                ('valid_to', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]