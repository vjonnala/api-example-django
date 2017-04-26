# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckOutSurveyResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.IntegerField()),
                ('q_explain', models.CharField(max_length=20, verbose_name=b'Did the doctor explain things in a way that was easy to understand?', choices=[(b'Yes, Definitely', b'Yes, Definitely'), (b'Yes, Somewhat', b'Yes, Somewhat'), (b'No', b'No')])),
                ('q_listening', models.CharField(max_length=20, verbose_name=b'Did the doctor listen carefully to you?', choices=[(b'Yes, Definitely', b'Yes, Definitely'), (b'Yes, Somewhat', b'Yes, Somewhat'), (b'No', b'No')])),
                ('q_instructions', models.CharField(max_length=20, verbose_name=b'Did the doctor seem to know the important information about your medical history?', choices=[(b'Yes, Definitely', b'Yes, Definitely'), (b'Yes, Somewhat', b'Yes, Somewhat'), (b'No', b'No')])),
                ('q_history', models.CharField(max_length=20, verbose_name=b'Did the doctor seem to know the important information about your medical history?', choices=[(b'Yes, Definitely', b'Yes, Definitely'), (b'Yes, Somewhat', b'Yes, Somewhat'), (b'No', b'No')])),
                ('q_respect', models.CharField(max_length=20, verbose_name=b'Did the doctor show respect for what you had to say?', choices=[(b'Yes, Definitely', b'Yes, Definitely'), (b'Yes, Somewhat', b'Yes, Somewhat'), (b'No', b'No')])),
            ],
        ),
    ]
