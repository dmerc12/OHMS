# Generated by Django 5.1 on 2024-10-02 17:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(255)])),
                ('description', models.CharField(blank=True, max_length=500, null=True, validators=[django.core.validators.MaxLengthValidator(500)])),
                ('size', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(255)])),
                ('unit_cost', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('available_quantity', models.PositiveIntegerField(default=0)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('name', 'size'), name='unique_material')],
            },
        ),
    ]
