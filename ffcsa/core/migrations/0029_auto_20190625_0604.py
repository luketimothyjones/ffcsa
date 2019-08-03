# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-25 13:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0028_auto_20190624_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='payment_agreement',
            field=models.BooleanField(default=False, verbose_name='I agree to make monthly payments in order to maintain my membership with the FFCSA for 12 months, with a minimium of $172 per month. If I need to change my monthly payment amount, I will notify the FFCSA admin and keep changes to a maximum of two times per year.'),
        ),
    ]