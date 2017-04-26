# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentStatusHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.IntegerField()),
                ('status', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='appointmentstatushistory',
            unique_together=set([('appointment', 'status')]),
        ),
    ]
