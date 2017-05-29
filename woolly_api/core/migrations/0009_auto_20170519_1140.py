# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-19 11:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20170518_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='item_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.ItemGroup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='woollyuser',
            name='type',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='core.WoollyUserType'),
        ),
    ]
