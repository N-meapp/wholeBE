# Generated by Django 5.1.5 on 2025-02-13 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailapp', '0009_customer_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='profile_image',
            field=models.ImageField(blank=True, upload_to='media/'),
        ),
    ]
