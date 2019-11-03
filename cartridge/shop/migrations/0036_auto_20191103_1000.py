# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-11-03 18:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0035_auto_20191103_0938'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vendorproductvariation',
            options={'verbose_name': 'Vendor Product Variation', 'verbose_name_plural': 'Vendor Product Variations'},
        ),
        migrations.RemoveField(
            model_name='vendorproductvariation',
            name='_order',
        ),
        migrations.AlterOrderWithRespectTo(
            name='vendorproductvariation',
            order_with_respect_to='variation',
        ),
    ]
