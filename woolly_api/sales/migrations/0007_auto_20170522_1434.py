# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-22 14:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_auto_20170522_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='group',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='sales.ItemGroup'),
        ),
    ]