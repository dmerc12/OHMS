# Generated by Django 4.2.14 on 2024-08-16 17:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(255)])),
                ('description', models.CharField(blank=True, max_length=500, null=True, validators=[django.core.validators.MaxLengthValidator(500)])),
            ],
        ),
    ]
