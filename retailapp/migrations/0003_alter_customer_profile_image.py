# Generated by Django 5.1.5 on 2025-02-26 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailapp', '0002_alter_customer_password_alter_customer_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='profile_image',
            field=models.ImageField(default='media/profile_w1sjxSH.jpg', upload_to='media/'),
        ),
    ]
