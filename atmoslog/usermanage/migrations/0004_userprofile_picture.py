# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanage', '0003_auto_20150806_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='picture',
            field=models.CharField(default='http://www.gravatar.com.avatar/000000000000000000000000000000?d=mm', max_length=200),
            preserve_default=False,
        ),
    ]
