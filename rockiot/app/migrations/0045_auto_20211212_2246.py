# Generated by Django 3.2.9 on 2021-12-12 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_auto_20211210_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aqcategory',
            name='pollutant',
            field=models.CharField(choices=[('TEMPERATURE', 'TEMPERATURE'), ('HUMIDITY', 'HUMIDITY'), ('PM1', 'PM1'), ('PM2_5', 'PM2_5'), ('PM10', 'PM10'), ('NO2', 'NO2'), ('SO2', 'SO2')], default='PM1', max_length=16),
        ),
        migrations.AlterField(
            model_name='aqclassification',
            name='description',
            field=models.TextField(),
        ),
    ]
