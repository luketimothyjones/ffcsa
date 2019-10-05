# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-05 13:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ffcsa_core', '0037_auto_20190826_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('session_key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='session key')),
                ('session_data', models.TextField(verbose_name='session data')),
                ('expire_date', models.DateTimeField(db_index=True, verbose_name='expire date')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'sessions',
                'verbose_name': 'session',
                'abstract': False,
            },
        ),
    ]
