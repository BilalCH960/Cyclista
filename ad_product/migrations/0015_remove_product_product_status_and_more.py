# Generated by Django 5.0.1 on 2024-02-26 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad_product', '0014_remove_product_featured_productvariant_featured'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_status',
        ),
        migrations.AddField(
            model_name='productvariant',
            name='product_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('disabled', 'Disabled'), ('rejected', 'Rejected'), ('in_review', 'In Review'), ('published', 'Published')], default='in_review', max_length=10),
        ),
    ]