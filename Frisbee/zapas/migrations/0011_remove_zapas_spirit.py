# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-27 22:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zapas', '0010_zapas_spirit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zapas',
            name='spirit',
        ),
    ]
