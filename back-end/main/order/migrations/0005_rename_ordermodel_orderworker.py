# Generated by Django 5.1 on 2024-10-05 02:26

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_alter_order_callout_alter_order_discount_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrderModel',
            new_name='OrderWorker',
        ),
    ]