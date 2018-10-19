# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_address',
            field=models.FileField(default='', upload_to=''),
        ),
        migrations.AddField(
            model_name='user',
            name='user_phone',
            field=models.FileField(max_length=11, default='', upload_to=''),
        ),
    ]
