# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-21 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20170826_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='attending_dinner',
            field=models.IntegerField(default=0),
        ),
    ]
