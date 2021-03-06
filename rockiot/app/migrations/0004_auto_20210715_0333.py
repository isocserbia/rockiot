# Generated by Django 3.2.5 on 2021-07-15 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20210715_0036'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=250)),
                ('address', models.CharField(max_length=250)),
                ('external_id', models.CharField(max_length=30)),
                ('external_key', models.CharField(max_length=50)),
                ('device_id', models.CharField(max_length=30)),
                ('device_key', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default='NEW', max_length=20)),
                ('mode', models.CharField(default='DEFAULT', max_length=20)),
                ('active', models.BooleanField(default=0)),
                ('metadata', models.JSONField()),
            ],
            options={
                'verbose_name_plural': 'Devices',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='researcher',
            options={'ordering': ['user'], 'verbose_name_plural': 'Researchers'},
        ),
        migrations.AlterModelOptions(
            name='visitor',
            options={'ordering': ['user'], 'verbose_name_plural': 'Visitors'},
        ),
    ]
