# Generated by Django 5.0.1 on 2024-03-20 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_alter_productreview_rating_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartorderitems',
            name='order',
        ),
        migrations.DeleteModel(
            name='CartOrder',
        ),
        migrations.DeleteModel(
            name='CartOrderItems',
        ),
    ]
