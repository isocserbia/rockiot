# Generated by Django 3.2.7 on 2021-09-02 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_rockiot_auth'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sensordata',
            options={'managed': False, 'ordering': ['-time'], 'verbose_name_plural': 'SensorData'},
        ),
        migrations.AlterModelOptions(
            name='sensordatalastvalues',
            options={'managed': False, 'ordering': ['-time'], 'verbose_name_plural': 'SensorDataLastValues'},
        ),
        migrations.RemoveField(
            model_name='device',
            name='device_key',
        ),
    ]

