# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanage', '0009_auto_20150809_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='recently_viewed_projects',
            field=models.TextField(default=b'[]'),
        ),
    ]
