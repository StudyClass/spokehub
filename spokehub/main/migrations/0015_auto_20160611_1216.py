# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-11 12:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['added']},
        ),
    ]