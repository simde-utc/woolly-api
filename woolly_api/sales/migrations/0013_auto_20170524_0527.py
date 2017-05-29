# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-24 05:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0012_delete_me'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemspecifications',
            name='woolly_user_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='sales.WoollyUserType'),
        ),
    ]