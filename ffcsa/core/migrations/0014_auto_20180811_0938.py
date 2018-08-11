# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-11 16:38
from __future__ import unicode_literals

import cartridge.shop.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0013_profile_paid_signup_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Invoice Notes'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='monthly_contribution',
            field=cartridge.shop.fields.MoneyField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Monthly Contribution'),
        ),
    ]
