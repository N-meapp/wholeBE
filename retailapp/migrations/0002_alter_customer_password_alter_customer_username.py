# Generated by Django 5.1.5 on 2025-02-26 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='password',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='customer',
            name='username',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
