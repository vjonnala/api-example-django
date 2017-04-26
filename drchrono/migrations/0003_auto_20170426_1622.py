# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0002_checkoutsurveyresponse'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'')),
                ('ordering', models.IntegerField(help_text=b'Enter a number to place this sign in order, displayed low to high')),
            ],
            options={
                'ordering': ['ordering'],
            },
        ),
        migrations.AlterField(
            model_name='checkoutsurveyresponse',
            name='q_instructions',
            field=models.CharField(max_length=20, verbose_name=b'Did the doctor give you easy to understand instructions about taking care of your health problems or concerns?', choices=[(b'Yes, Definitely', b'Yes, Definitely'), (b'Yes, Somewhat', b'Yes, Somewhat'), (b'No', b'No')]),
        ),
    ]
