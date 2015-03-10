# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0005_auto_20150202_1135'),
        ('geokey_epicollect', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EpiCollectMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_name', models.CharField(max_length=500)),
                ('contribution', models.ForeignKey(to='contributions.Observation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
