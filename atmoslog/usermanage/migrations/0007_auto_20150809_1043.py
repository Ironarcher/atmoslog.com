# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanage', '0006_auto_20150806_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='showemail',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='liked_projects',
            field=models.TextField(default=b'[]'),
        ),
    ]
