import os

from django.db import connection, migrations


def create_functions(apps, schema_editor):
    file_path = os.path.join(os.path.dirname(__file__), 'sql/', 'functions.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.execute(sql_statement)


def create_cron_jobs(apps, schema_editor):
    file_path = os.path.join(os.path.dirname(__file__), 'sql/', 'jobs.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.execute(sql_statement)


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0032_auto_20210920_1909'),
    ]

    operations = [
        migrations.RunPython(create_functions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(create_cron_jobs, reverse_code=migrations.RunPython.noop),
    ]
