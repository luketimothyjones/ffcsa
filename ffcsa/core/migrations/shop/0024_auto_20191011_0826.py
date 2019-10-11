# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-11 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0023_auto_20190827_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='in_inventory',
            field=models.BooleanField(default=False, verbose_name='FFCSA Inventory'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='in_inventory',
            field=models.BooleanField(default=False, verbose_name='FFCSA Inventory'),
        ),
        migrations.AddField(
            model_name='product',
            name='in_inventory',
            field=models.BooleanField(default=False, verbose_name='FFCSA Inventory'),
        ),
        migrations.AddField(
            model_name='productvariation',
            name='in_inventory',
            field=models.BooleanField(default=False, verbose_name='FFCSA Inventory'),
        ),
    ]
