# Generated by Django 5.0.1 on 2024-01-24 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
