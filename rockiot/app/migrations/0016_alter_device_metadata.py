# Generated by Django 3.2.6 on 2021-08-09 15:51

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20210809_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='metadata',
            field=models.JSONField(default=app.models.default_device_metadata),
        ),
    ]