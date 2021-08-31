# Generated by Django 2.2.5 on 2019-09-18 22:15
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.db import migrations
from django.contrib.auth import get_user_model

from django.contrib.auth.management import create_permissions
from django.utils.timezone import make_aware


def update_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def add_users(apps, schema_editor):

    User = get_user_model()

    add_device = Permission.objects.get(codename="add_device")
    change_device = Permission.objects.get(codename="change_device")
    view_device = Permission.objects.get(codename="view_device")
    view_deviceconnection = Permission.objects.get(codename="view_deviceconnection")
    view_facility = Permission.objects.get(codename="view_facility")
    view_facilitymembership = Permission.objects.get(codename="view_facilitymembership")
    view_municipality = Permission.objects.get(codename="view_municipality")
    view_platform = Permission.objects.get(codename="view_platform")
    view_platformattribute = Permission.objects.get(codename="view_platformattribute")

    view_sensordata = Permission.objects.get(codename="view_sensordata")
    view_sensordatalastvalues = Permission.objects.get(codename="view_sensordatalastvalues")

    researcher_group = Group(name="RESEARCHER")
    researcher_group.save()

    platform_admin_group = Group(name="PLATFORM_ADMIN")
    platform_admin_group.save()

    device_installer_group = Group(name="DEVICE_INSTALLER")
    device_installer_group.save()
    device_installer_group.permissions.add(view_device)
    device_installer_group.permissions.add(add_device)
    device_installer_group.permissions.add(change_device)
    device_installer_group.save()

    device_admin_group = Group(name="DEVICE_ADMIN")
    device_admin_group.save()
    device_admin_group.permissions.add(view_device)
    device_admin_group.permissions.add(add_device)
    device_admin_group.permissions.add(change_device)
    device_admin_group.permissions.add(view_deviceconnection)
    device_admin_group.permissions.add(view_facility)
    device_admin_group.permissions.add(view_facilitymembership)
    device_admin_group.permissions.add(view_municipality)
    device_admin_group.permissions.add(view_platform)
    device_admin_group.permissions.add(view_platformattribute)
    device_admin_group.save()

    api_user_group = Group(name="API_USER")
    api_user_group.save()
    api_user_group.permissions.add(view_sensordata)
    api_user_group.permissions.add(view_sensordatalastvalues)
    api_user_group.save()

    device_installer = User.objects.create_user(username='deviceinstaller',
                                                email="deviceinstaller@rockiot.rs",
                                                password="deviceinstaller123",
                                                is_staff=True,
                                                last_login=make_aware(datetime.now()))
    device_installer.groups.add(device_installer_group)
    device_installer.save()

    device_admin = User.objects.create_user(username='deviceadmin',
                                            email="deviceadmin@rockiot.rs",
                                            password="deviceadmin123",
                                            is_staff=True,
                                            last_login=make_aware(datetime.now()))
    device_admin.groups.add(device_admin_group)
    device_admin.save()

    api_user = User.objects.create_user(username='apiuser',
                                        email="apiuser@rockiot.rs",
                                        password="apiuser123",
                                        is_staff=False,
                                        last_login=make_aware(datetime.now()))
    api_user.groups.add(api_user_group)
    api_user.save()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0028_initialdata')
    ]

    operations = [
        migrations.RunPython(update_permissions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(add_users, reverse_code=migrations.RunPython.noop)

    ]
