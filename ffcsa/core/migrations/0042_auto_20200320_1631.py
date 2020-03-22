# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-20 23:31
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0041_auto_20200320_1611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='delivery_zip_code',
        ),
        migrations.AddField(
            model_name='profile',
            name='delivery_zipcode',
            field=models.CharField(blank=True, max_length=5, validators=[django.core.validators.RegexValidator(message='Invalid zipcode', regex='^\\d{5}$')], verbose_name='Zipcode'),
        ),
    ]