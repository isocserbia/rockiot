# Generated by Django 3.2.8 on 2021-10-27 14:29

import app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_sensor_average'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorDayAverageFacility',
            fields=[
                ('code', models.CharField(max_length=30)),
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=16)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=16)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm1', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm2_5', models.DecimalField(decimal_places=4, max_digits=16)),
            ],
            options={
                'verbose_name_plural': 'SensorDayAverageFacilities',
                'db_table': 'sensor_data_day_average_facility',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SensorDayAverageMunicipality',
            fields=[
                ('code', models.CharField(max_length=30)),
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=16)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=16)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm1', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm2_5', models.DecimalField(decimal_places=4, max_digits=16)),
            ],
            options={
                'verbose_name_plural': 'SensorDayAverageMunicipality',
                'db_table': 'sensor_data_day_average_municipality',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SensorHourAverageFacility',
            fields=[
                ('code', models.CharField(max_length=30)),
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=16)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=16)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm1', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm2_5', models.DecimalField(decimal_places=4, max_digits=16)),
            ],
            options={
                'verbose_name_plural': 'SensorHourAverageFacilities',
                'db_table': 'sensor_data_hour_average_facility',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SensorHourAverageMunicipality',
            fields=[
                ('code', models.CharField(max_length=30)),
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=16)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=16)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm1', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=16)),
                ('pm2_5', models.DecimalField(decimal_places=4, max_digits=16)),
            ],
            options={
                'verbose_name_plural': 'class SensorHourAverageMunicipalities',
                'db_table': 'sensor_data_hour_average_municipality',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AlertScheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('scheme', models.JSONField(default=app.models.default_alert_scheme)),
            ],
            options={
                'verbose_name': 'DeviceAlertScheme',
                'verbose_name_plural': 'DeviceAlertSchemes',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='device',
            name='alert_scheme',
            field=models.ForeignKey(db_column='alert_scheme_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='app.alertscheme'),
        ),
        migrations.AddField(
            model_name='devicelogentry',
            name='alert_scheme',
            field=models.ForeignKey(blank=True, db_column='alert_scheme_id', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='app.alertscheme'),
        ),
    ]