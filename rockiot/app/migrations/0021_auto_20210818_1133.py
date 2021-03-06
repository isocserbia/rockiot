# Generated by Django 3.2.6 on 2021-08-18 11:33

import app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20210817_0507'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilitySensorsSummaryMinute',
            fields=[
                ('slug', models.CharField(max_length=30)),
                ('bucket', models.DateTimeField(primary_key=True, serialize=False)),
                ('avg_temp', models.DecimalField(decimal_places=4, max_digits=8)),
                ('avg_humidity', models.DecimalField(decimal_places=4, max_digits=8)),
                ('avg_co', models.DecimalField(decimal_places=4, max_digits=8)),
                ('avg_smoke', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'FacilitySensorsSummaryMinute',
                'db_table': 'educational_facility_summary_minute',
                'ordering': ['bucket'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LagDiffCo',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('diff_perc', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'LagDiffCo',
                'db_table': 'lag_diff_co',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LagDiffHumidity',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('diff_perc', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'LagDiffHumidity',
                'db_table': 'lag_diff_humidity',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LagDiffSmoke',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('diff_perc', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'LagDiffSmoke',
                'db_table': 'lag_diff_smoke',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LagDiffTemperature',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('diff_perc', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'LagDiffTemperatures',
                'db_table': 'lag_diff_temperature',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SensorsSummaryMinute',
            fields=[
                ('bucket', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('avg_temp', models.DecimalField(decimal_places=4, max_digits=8)),
                ('avg_humidity', models.DecimalField(decimal_places=4, max_digits=8)),
                ('avg_co', models.DecimalField(decimal_places=4, max_digits=8)),
                ('avg_smoke', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'SensorsSummaryMinute',
                'db_table': 'sensors_summary_minute',
                'ordering': ['bucket'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DeviceConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('user', models.CharField(max_length=64)),
                ('client_id', models.CharField(max_length=64)),
                ('ip_address', models.CharField(max_length=64)),
                ('msg_cnt', models.DecimalField(decimal_places=0, max_digits=8)),
                ('msg_rate', models.DecimalField(decimal_places=2, max_digits=8)),
                ('connected_at', models.DateTimeField()),
                ('terminated_at', models.DateTimeField()),
                ('faults', models.JSONField(default=app.models.default_device_connection_faults)),
                ('device', models.ForeignKey(db_column='device_id', on_delete=django.db.models.deletion.CASCADE, related_name='connections', to='app.device')),
            ],
            options={
                'verbose_name_plural': 'Device connections',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='platform',
            options={'ordering': ['name'], 'verbose_name_plural': 'Platform'},
        ),
        migrations.AlterModelTable(
            name='sensordata',
            table='sensor_data',
        ),
        migrations.DeleteModel(
            name='HealthIndicator',
        ),
    ]
