from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20210822_2000'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorsDataRollup1h',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=8)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=8)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm25', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'SensorsDataRollup1h',
                'db_table': 'sensor_data_rollup_1h',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SensorsDataRollup24h',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=8)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=8)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm25', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'SensorsDataRollup24h',
                'db_table': 'sensor_data_rollup_24h',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SensorsDataRollup4h',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=8)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=8)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm25', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'SensorsDataRollup4h',
                'db_table': 'sensor_data_rollup_4h',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SensorsDataRollup5m',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=30)),
                ('temperature', models.DecimalField(decimal_places=4, max_digits=8)),
                ('humidity', models.DecimalField(decimal_places=4, max_digits=8)),
                ('no2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('so2', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm10', models.DecimalField(decimal_places=4, max_digits=8)),
                ('pm25', models.DecimalField(decimal_places=4, max_digits=8)),
            ],
            options={
                'verbose_name_plural': 'SensorsDataRollup5m',
                'db_table': 'sensor_data_rollup_5m',
                'abstract': False,
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CronJob',
            fields=[
                ('jobid', models.IntegerField(primary_key=True, serialize=False)),
                ('schedule', models.CharField(max_length=128)),
                ('command', models.TextField()),
                ('nodename', models.CharField(max_length=64)),
                ('nodeport', models.IntegerField()),
                ('database', models.CharField(max_length=64)),
                ('username', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('jobname', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name_plural': 'Data jobs',
                'db_table': 'cron\".\"job',
                'ordering': ['jobid'],
                'managed': False
            },
        ),
        migrations.CreateModel(
            name='CronJobExecution',
            fields=[
                ('runid', models.IntegerField(primary_key=True, serialize=False)),
                ('job_pid', models.IntegerField()),
                ('database', models.CharField(max_length=64)),
                ('username', models.CharField(max_length=64)),
                ('command', models.TextField()),
                ('status', models.CharField(max_length=128)),
                ('return_message', models.CharField(max_length=64)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('jobid', models.ForeignKey(db_column='jobid', on_delete=django.db.models.deletion.CASCADE, related_name='executions', to='app.cronjob')),
            ],
            options={
                'verbose_name_plural': 'Executions',
                'db_table': 'cron\".\"job_run_details',
                'ordering': ['jobid', 'runid'],
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='SensorsSummary15Minute',
        ),
        migrations.DeleteModel(
            name='SensorsSummary4Hour',
        ),
        migrations.DeleteModel(
            name='SensorsSummaryDay',
        ),
        migrations.DeleteModel(
            name='SensorsSummaryHour',
        ),
        migrations.DeleteModel(
            name='SensorsSummaryMinute',
        ),
    ]
