# Generated by Django 5.0.1 on 2024-05-07 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='referral_code',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]