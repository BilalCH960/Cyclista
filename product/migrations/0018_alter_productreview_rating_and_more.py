# Generated by Django 5.0.1 on 2024-03-18 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_alter_productreview_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(1, '⭐'), (2, '⭐⭐'), (3, '⭐⭐⭐'), (4, '⭐⭐⭐⭐'), (5, '⭐⭐⭐⭐⭐')], default=None),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='review',
            field=models.TextField(default=None),
        ),
    ]
