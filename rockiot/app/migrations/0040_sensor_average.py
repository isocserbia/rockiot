import os

from django.db import connection, migrations


def create_views(apps, schema_editor):
    file_path = os.path.join(os.path.dirname(__file__), 'sql/', 'sensor_average.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.execute(sql_statement)


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0039_auto_20211015_1658'),
    ]

    operations = [
        migrations.RunPython(create_views, reverse_code=migrations.RunPython.noop),
    ]
