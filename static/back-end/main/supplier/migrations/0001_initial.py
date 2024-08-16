# Generated by Django 4.2.14 on 2024-08-16 21:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(255)])),
                ('notes', models.CharField(blank=True, max_length=500, null=True, validators=[django.core.validators.MaxLengthValidator(500)])),
            ],
        ),
        migrations.CreateModel(
            name='SupplierAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(255)])),
                ('city', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(100)])),
                ('state', models.CharField(max_length=13, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(13)])),
                ('zip', models.PositiveIntegerField()),
                ('notes', models.CharField(blank=True, max_length=500, null=True, validators=[django.core.validators.MaxLengthValidator(500)])),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplier.supplier')),
            ],
        ),
    ]
