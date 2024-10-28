# Generated by Django 5.1 on 2024-10-27 22:03

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
        ('material', '0001_initial'),
        ('service', '0001_initial'),
        ('tool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderWorkLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('description', models.CharField(max_length=2000, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(2000)])),
                ('hourly_rate', models.DecimalField(decimal_places=2, default=93.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('75'))])),
                ('hours_worked', models.DecimalField(decimal_places=2, default=3.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('3'))])),
                ('labor_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('material_upcharge', models.DecimalField(decimal_places=2, default=25.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('15')), django.core.validators.MaxValueValidator(Decimal('75'))])),
                ('material_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('line_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('subtotal', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('tax', models.DecimalField(decimal_places=2, default=12.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('20'))])),
                ('tax_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('completed', models.BooleanField(default=False)),
                ('paid', models.BooleanField(default=False)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))])),
                ('discount_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('payment_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('working_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('notes', models.CharField(blank=True, max_length=10000, null=True, validators=[django.core.validators.MaxLengthValidator(10000)])),
                ('callout', models.FloatField(choices=[('50.0', 'Standard - $50.00'), ('175.0', 'Emergency - $175.00')], default='50.0')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.service')),
            ],
        ),
        migrations.CreateModel(
            name='OrderCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(300)])),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='order.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='material.material')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='order.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('type', models.CharField(choices=[('cash', 'Cash'), ('check', 'Check')], max_length=5)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('notes', models.CharField(blank=True, max_length=255, null=True, validators=[django.core.validators.MaxLengthValidator(255)])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='order.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderPicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='orders')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='order.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderTool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_used', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('quantity_broken', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tools', to='order.order')),
                ('tool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.tool')),
            ],
        ),
        migrations.CreateModel(
            name='OrderWorker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workers', to='order.order')),
            ],
        ),
    ]
