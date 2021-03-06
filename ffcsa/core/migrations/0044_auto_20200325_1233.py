# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-25 19:33
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ffcsa_core', '0043_auto_20200325_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='join_dairy_program',
            field=models.BooleanField(default=False, help_text="I would like to join the Raw Dairy program. I understand that I will be charged a $50 herd-share fee when making my first payment and will need to talk to the Dairy Manager before gaining access to raw dairy products. We'll be in touch soon.", verbose_name='Join Raw Dairy Program'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='num_adults',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='How many adults are in your family?'),
        ),
    ]
