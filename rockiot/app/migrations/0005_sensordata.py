# Generated by Django 3.2.5 on 2021-07-20 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210715_0333'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('device_id', models.CharField(max_length=30)),
                ('temperature', models.DecimalField(decimal_places=3, max_digits=7)),
                ('humidity', models.DecimalField(decimal_places=3, max_digits=7)),
                ('co', models.DecimalField(decimal_places=3, max_digits=7)),
                ('smoke', models.DecimalField(decimal_places=3, max_digits=7)),
            ],
            options={
                'verbose_name_plural': 'SensorData',
                'db_table': 'app_sensor_data',
                'ordering': ['time'],
            },
        ),
    ]
