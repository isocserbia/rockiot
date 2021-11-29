from django.core.exceptions import ValidationError
from dynamic_preferences.types import BooleanPreference, LongStringPreference, IntegerPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry

general = Section('general')
device = Section('device')


# We start with a global preference
@global_preferences_registry.register
class MembershipSecurity(BooleanPreference):
    section = general
    name = 'facility_membership_security'
    default = False
    required = False
    help_text = 'Configures if Facility membership is required to perform Devices actions belonging to Facility. NOT IN USE'


@global_preferences_registry.register
class MetadataDevicesLogsDeletionAfterDays(IntegerPreference):
    section = general
    name = 'metadata_devices_logs_deletion_after_days'
    default = 90
    required = True
    help_text = 'Configures after how many days metadata changes in devices logs are deleted'


@user_preferences_registry.register
class DeviceTableColumns(LongStringPreference):
    section = device
    name = 'table_columns'
    default = 'device_id, name, facility, municipality, mode, activation_status, state'
    required = False
    help_text = 'Configures columns on Device list view. Available columns: name, facility__name, facility__municipality__name, device_id, status, mode, created_at, updated_at, last_event_sent_at, alert_scheme__name, all metadata fields: metadata__device_fw, metadata__sent_at, metadata__no2_ready, metadata__so2_ready, metadata__no2_online, metadata__so2_online, metadata__pms_online etc'

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
    help_text = 'Configures which columns are links to Device view on Devices list view. Columns must exist and be enabled'

    def validate(self, value):
        if not value.startswith('device_id'):
            raise ValidationError('Column device_id is mandatory')
        else:
            super().validate(value)


@user_preferences_registry.register
class DeviceTableFilter(LongStringPreference):
    section = device
    name = 'table_filter'
    default = 'facility, status, mode'
    required = False
    help_text = 'Configures available filters for Devices list view. Columns must exist and be enabled. Available filters: device_id, facility, status, mode, device_fw, no2_ready, so2_ready, no2_online, so2_online, pms_online'


@user_preferences_registry.register
class DeviceFormSectionOrder(LongStringPreference):
    section = device
    name = 'form_sections'
    default = 'Location, Metadata, Confidential'
    required = False
    help_text = 'Configures displayed sections on Device view as well as order of section'


@user_preferences_registry.register
class DeviceFormLocationOpened(BooleanPreference):
    section = device
    name = 'form_location_opened'
    default = True
    required = False
    help_text = 'Configures if Location section is initially displayed on Device view'
