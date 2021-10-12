import os

from django.db import connection, migrations


def load_data_from_sql(apps, schema_editor):
    file_path = os.path.join(os.path.dirname(__file__), 'sql/', 'theme.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.execute(sql_statement)


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0025_auto_20210825_2025'),
    ]

    operations = [
        migrations.RunPython(load_data_from_sql, reverse_code=migrations.RunPython.noop),
    ]
