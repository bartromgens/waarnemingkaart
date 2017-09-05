# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-05 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('observation', '0005_auto_20170902_0003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ['name_nl']},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ['name_nl']},
        ),
        migrations.AlterModelOptions(
            name='observation',
            options={'ordering': ['species']},
        ),
        migrations.AlterModelOptions(
            name='species',
            options={'ordering': ['name_nl']},
        ),
        migrations.AddField(
            model_name='family',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='observation.Group'),
        ),
        migrations.AddField(
            model_name='species',
            name='family',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='observation.Family'),
        ),
    ]
