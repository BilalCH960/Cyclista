# Generated by Django 5.0.1 on 2024-02-25 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad_product', '0011_alter_product_color'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productvariant',
            old_name='screen_size',
            new_name='size',
        ),
        migrations.RemoveField(
            model_name='product',
            name='color',
        ),
        migrations.RemoveField(
            model_name='product',
            name='offer_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='stock_count',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='os',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='ram',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='storage',
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('disabled', 'Disabled'), ('rejected', 'Rejected'), ('in_review', 'In Review'), ('published', 'Published')], default='in_review', max_length=10),
        ),
    ]
