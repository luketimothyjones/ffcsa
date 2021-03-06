# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-23 12:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0041_profile_join_dairy_program'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='join_dairy_program',
            field=models.BooleanField(default=False, help_text='I would like to join the Raw Dairy program. I understand that I will be charged a $50 herd-share fee when making my first payment to gain access to raw dairy products.', verbose_name='Join Raw Dairy Program'),
        ),
    ]
