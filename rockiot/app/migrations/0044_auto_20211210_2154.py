# Generated by Django 3.2.9 on 2021-12-10 21:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_auto_20211030_2209'),
    ]

    operations = [
        migrations.CreateModel(
            name='AqCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('pollutant', models.CharField(max_length=16)),
                ('timeframe', models.CharField(choices=[('1h', '1h'), ('4h', '4h'), ('24h', '24h'), ('15m', '15m')], default='1h', max_length=10)),
                ('lower_limit', models.IntegerField()),
                ('upper_limit', models.IntegerField()),
            ],
            options={
                'db_table': 'aq_category',
            },
        ),
        migrations.CreateModel(
            name='AqClassification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'aq_classification',
            },
        ),
        migrations.AddField(
            model_name='aqcategory',
            name='classification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='app.aqclassification'),
        ),
    ]