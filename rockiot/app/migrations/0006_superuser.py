import os
from datetime import datetime

from django.db import migrations
from django.utils.timezone import make_aware


def generate_superuser(apps, schema_editor):

    from django.contrib.auth.models import User

    su_name = os.environ.get('DJANGO_SU_NAME', default='admin')
    su_email = os.environ.get('DJANGO_SU_EMAIL', default='admin@rockiot.org')
    su_pass = os.environ.get('DJANGO_SU_PASS', default='admin')
    superuser = User.objects.create_superuser(su_name,
                                              email=su_email,
                                              password=su_pass,
                                              last_login=make_aware(datetime.utcnow()))
    superuser.save()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_sensordata'),
    ]

    operations = [
        migrations.RunPython(generate_superuser),
    ]
