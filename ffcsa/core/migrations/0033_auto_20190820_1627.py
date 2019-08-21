# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-20 23:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0032_auto_20190817_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='charge_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='google_person_id',
            field=models.TextField(blank=True, help_text='Google Person resource id', null=True),
        ),
    ]
