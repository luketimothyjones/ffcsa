# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-27 17:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0044_auto_20200325_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='product_agreement',
        ),
    ]
