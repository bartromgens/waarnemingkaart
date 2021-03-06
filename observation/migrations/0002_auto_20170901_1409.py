# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-01 12:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordinates',
            name='lat',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='coordinates',
            name='lon',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='family',
            name='name',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='family',
            name='name_latin',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='family',
            name='name_nl',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='group',
            name='name_latin',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='group',
            name='name_nl',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='observation',
            name='url',
            field=models.URLField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='name',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='species',
            name='name_latin',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='species',
            name='name_nl',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
