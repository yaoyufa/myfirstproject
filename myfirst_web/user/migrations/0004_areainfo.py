# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20181016_0721'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('atitle', models.CharField(max_length=30)),
                ('aParent', models.ForeignKey(to='user.AreaInfo', null=True, blank=True)),
            ],
        ),
    ]
