# Generated by Django 5.0.1 on 2024-05-21 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0003_alter_referral_my_referral_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='my_referral',
            field=models.CharField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='referral',
            name='referral_code',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]