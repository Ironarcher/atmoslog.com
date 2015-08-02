# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('about_me', models.CharField(max_length=500)),
                ('fav_language', models.CharField(max_length=6, choices=[(b'?', b'Undecided'), (b'py', b'Python'), (b'c++', b'C++'), (b'c#', b'C#'), (b'java', b'Java'), (b'php', b'PHP'), (b'ruby', b'Ruby'), (b'obj-c', b'Objective-C'), (b'c', b'C'), (b'vb', b'Visual Basic'), (b'javasc', b'Javascript'), (b'perl', b'Perl'), (b'assem', b'Assembly'), (b'r', b'R'), (b'swift', b'Swift'), (b'pascal', b'Pascal'), (b'scala', b'Scala'), (b'go', b'Go')])),
                ('joined_on', models.DateField(auto_now_add=True)),
                ('liked_projects', models.TextField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
