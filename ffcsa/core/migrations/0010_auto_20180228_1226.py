# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-02-28 20:26
from __future__ import unicode_literals

import ffcsa.shop.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0009_auto_20180111_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='monthly_contribution',
            field=ffcsa.shop.fields.MoneyField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Default Monthly Contribution'),
        ),
    ]
