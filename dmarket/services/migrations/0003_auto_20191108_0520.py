# Generated by Django 2.1.13 on 2019-11-08 05:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_auto_20191108_0518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 8, 5, 20, 36, 576219, tzinfo=utc)),
        ),
    ]
