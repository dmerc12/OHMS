# Generated by Django 5.1 on 2024-10-08 20:19

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_alter_order_callout'),
        ('tool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderTool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tools', to='order.order')),
                ('tool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.tool')),
            ],
        ),
    ]