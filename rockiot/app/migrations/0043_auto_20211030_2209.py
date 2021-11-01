from django.db import migrations

from app.models import AlertScheme, Device


def create_default_scheme(apps, schema_editor):
    record = AlertScheme(name="Default")
    record.save()


def update_devices(apps, schema_editor):
    scheme = AlertScheme.objects.first()
    count = Device.objects.filter(alert_scheme__isnull=True).update(alert_scheme=scheme)
    print(f"Updated {count} devices with default alert scheme")


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0042_auto_20211030_2009'),
    ]

    operations = [
        migrations.RunPython(create_default_scheme, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(update_devices, reverse_code=migrations.RunPython.noop),
    ]