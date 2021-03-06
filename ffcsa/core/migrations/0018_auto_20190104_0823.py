# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-01-04 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0017_payment_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='pending',
            field=models.BooleanField(default=False, verbose_name='Pending'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
    ]
