import os

from django.db import connection, migrations


def create_periodic_tasks(apps, schema_editor):
    file_path = os.path.join(os.path.dirname(__file__), '../sql/', 'celery.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.execute(sql_statement)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency("django_celery_beat.PeriodicTask"),
        ('django_celery_beat', '0014_remove_clockedschedule_enabled'),
        ('app', '0033_rollup_functions_jobs'),
    ]

    operations = [
        migrations.RunPython(create_periodic_tasks, reverse_code=migrations.RunPython.noop),
    ]
