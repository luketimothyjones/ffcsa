# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-02-03 01:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invites', '0002_invitationcode_drop_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitationcode',
            name='non_subscribing_member',
            field=models.BooleanField(default=False, help_text='Non-subscribing members are allowed to make payments to their ffcsa account w/o having a monthly subscription'),
        ),
    ]
