# Generated by Django 3.2.6 on 2021-08-06 17:25
from collections import defaultdict

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20210806_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='metadata',
            field=models.JSONField(blank=True, default=defaultdict(list), null=True),
        ),
    ]