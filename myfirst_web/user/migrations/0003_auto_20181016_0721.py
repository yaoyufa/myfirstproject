# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20181016_0156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='user_address',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='address',
            name='user_phone',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='address',
            name='user_postcode',
            field=models.CharField(max_length=6),
        ),
        migrations.AlterField(
            model_name='address',
            name='user_recipient',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_address',
            field=models.CharField(max_length=100, default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_phone',
            field=models.CharField(max_length=11, default=''),
        ),
    ]
