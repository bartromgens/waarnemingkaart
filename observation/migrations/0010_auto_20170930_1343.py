# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-30 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observation', '0009_auto_20170930_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observer',
            name='name',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
    ]
