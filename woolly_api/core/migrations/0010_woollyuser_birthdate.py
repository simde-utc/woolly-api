# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-26 08:28
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20170526_0706'),
    ]

    operations = [
        migrations.AddField(
            model_name='woollyuser',
            name='birthdate',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
