# Generated by Django 3.2.6 on 2021-08-30 18:55

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0026_theme'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.SlugField(default="", max_length=64, unique=True)),
                ('type', models.CharField(choices=[('ELEMENTARY_SCHOOL', 'ELEMENTARY_SCHOOL'), ('HIGH_SCHOOL', 'HIGH_SCHOOL'), ('FACULTY', 'FACULTY'), ('UNIVERSITY', 'UNIVERSITY')], default='ELEMENTARY_SCHOOL', max_length=20)),
                ('email', models.EmailField(max_length=120)),
                ('description', models.TextField(blank=True, null=True)),
                ('address', models.CharField(max_length=250)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Facility',
                'verbose_name_plural': 'Facilities',
                'ordering': ['name'],
            },
        ),
        migrations.RenameModel(
            old_name='ServerAttribute',
            new_name='PlatformAttribute',
        ),
        migrations.AlterModelOptions(
            name='deviceconnection',
            options={'ordering': ['-connected_at'], 'verbose_name_plural': 'Device connections'},
        ),
        migrations.AlterModelOptions(
            name='platformattribute',
            options={'ordering': ['name'], 'verbose_name': 'Platform attribute', 'verbose_name_plural': 'Platform attributes'},
        ),
        migrations.RemoveField(
            model_name='device',
            name='address',
        ),
        migrations.RemoveField(
            model_name='device',
            name='educational_facility',
        ),
        migrations.RemoveField(
            model_name='device',
            name='ip_address',
        ),
        migrations.RemoveField(
            model_name='device',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='device',
            name='lon',
        ),
        migrations.RenameModel(
            old_name='EducationalFacilityMembership',
            new_name='FacilityMembership',
        ),
        migrations.RemoveField(
            model_name='facilitymembership',
            name='educational_facility',
        ),
        migrations.AlterField(
            model_name='deviceconnection',
            name='state',
            field=models.CharField(default='UNKNOWN', max_length=30),
        ),
        migrations.AlterField(
            model_name='municipality',
            name='code',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='deviceconnection',
            unique_together={('name', 'client_id')},
        ),
        migrations.DeleteModel(
            name='EducationFacility',
        ),
        migrations.AddField(
            model_name='facility',
            name='municipality',
            field=models.ForeignKey(db_column='municipality_id', on_delete=django.db.models.deletion.PROTECT, related_name='facilities', to='app.municipality'),
        ),
        migrations.AddField(
            model_name='facility',
            name='users',
            field=models.ManyToManyField(through='app.FacilityMembership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='device',
            name='facility',
            field=models.ForeignKey(db_column='facility_id', default=1, on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='app.facility'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='facilitymembership',
            name='facility',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.facility'),
            preserve_default=False,
        ),
    ]