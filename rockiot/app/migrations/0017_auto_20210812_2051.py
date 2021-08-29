# Generated by Django 3.2.6 on 2021-08-12 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_device_metadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Platforms',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='device',
            name='educational_facility',
            field=models.ForeignKey(db_column='education_facility_id', on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='app.educationfacility'),
        ),
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.CharField(choices=[('NEW', 'NEW'), ('REGISTERED', 'REGISTERED'), ('ACTIVATED', 'ACTIVATED'), ('DEACTIVATED', 'DEACTIVATED'), ('TERMINATED', 'TERMINATED')], default='NEW', max_length=20),
        ),
        migrations.AlterField(
            model_name='educationfacility',
            name='municipality',
            field=models.ForeignKey(db_column='municipality_id', on_delete=django.db.models.deletion.PROTECT, related_name='facilities', to='app.municipality'),
        ),
        migrations.CreateModel(
            name='ServerAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('platform', models.ForeignKey(db_column='platform_id', on_delete=django.db.models.deletion.PROTECT, related_name='attributes', to='app.platform')),
            ],
            options={
                'verbose_name_plural': 'Server attributes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HealthIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('platform', models.ForeignKey(db_column='platform_id', on_delete=django.db.models.deletion.PROTECT, related_name='indicators', to='app.platform')),
            ],
            options={
                'verbose_name_plural': 'Health indicators',
                'ordering': ['name'],
            },
        ),
    ]
