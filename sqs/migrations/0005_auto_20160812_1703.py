# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sqs', '0004_studentanswers_quiz_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='school',
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.CharField(default=b'student', max_length=100),
        ),
        migrations.DeleteModel(
            name='Teacher',
        ),
    ]
