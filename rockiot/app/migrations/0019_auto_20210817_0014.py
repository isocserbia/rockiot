# Generated by Django 3.2.6 on 2021-08-17 00:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0017_auto_20210812_2051'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationalFacilityMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('educational_facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.educationfacility')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='visitor',
            name='user',
        ),
        migrations.DeleteModel(
            name='Researcher',
        ),
        migrations.DeleteModel(
            name='Visitor',
        ),
        migrations.AddField(
            model_name='educationfacility',
            name='users',
            field=models.ManyToManyField(through='app.EducationalFacilityMembership', to=settings.AUTH_USER_MODEL),
        ),
    ]

