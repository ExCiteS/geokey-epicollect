# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20150202_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='EpiCollectProject',
            fields=[
                ('enabled', models.BooleanField(default=False)),
                ('project', models.OneToOneField(related_name='epicollect', primary_key=True, serialize=False, to='projects.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
