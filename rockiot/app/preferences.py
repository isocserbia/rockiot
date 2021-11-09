from django.core.exceptions import ValidationError
from dynamic_preferences.types import BooleanPreference, StringPreference, LongStringPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry

general = Section('general')
device = Section('device')


# We start with a global preference
@global_preferences_registry.register
class MaintenanceMode(BooleanPreference):
    name = 'maintenance_mode'
    default = False


@user_preferences_registry.register
class DeviceTableColumns(LongStringPreference):
    section = device
    name = 'table_columns'
    default = 'device_id, name, facility, municipality, mode, activation_status, state'
    required = False

    def validate(self, value):
        if not value.startswith('device_id'):
            raise ValidationError('Column device_id is mandatory')
        else:
            super().validate(value)


@user_preferences_registry.register
class DeviceTableColumnsLink(LongStringPreference):
    section = device
    name = 'table_columns_links'
    default = 'device_id, name'
    required = False

    def validate(self, value):
        if not value.startswith('device_id'):
            raise ValidationError('Column device_id is mandatory')
        else:
            super().validate(value)


@user_preferences_registry.register
class DeviceTableFilter(LongStringPreference):
    section = device
    name = 'table_filter'
    default = 'status, mode'
    required = False
