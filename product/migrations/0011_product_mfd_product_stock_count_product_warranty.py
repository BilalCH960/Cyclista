# Generated by Django 5.0.1 on 2024-02-03 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_alter_productimages_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='mfd',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_count',
            field=models.CharField(blank=True, default='10', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='warranty',
            field=models.CharField(blank=True, default='6 months', max_length=100, null=True),
        ),
    ]
