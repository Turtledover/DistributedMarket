# Generated by Django 2.1.13 on 2019-10-29 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_auto_20191029_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='start_time',
            field=models.DateTimeField(),
        ),
    ]
