from collections import OrderedDict
from datetime import datetime
from functools import reduce

from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import Q
from django.forms import TextInput, Textarea, ModelForm
from django.utils.html import format_html
from django_celery_beat.models import SolarSchedule, ClockedSchedule
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import GroupResult, TaskResult
from dynamic_preferences.admin import GlobalPreferenceAdmin, DynamicPreferenceAdmin
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.settings import preferences_settings
from dynamic_preferences.users.admin import UserPreferenceAdmin
from dynamic_preferences.users.forms import UserSinglePreferenceForm
from dynamic_preferences.users.models import UserPreferenceModel
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from simple_history.admin import SimpleHistoryAdmin
from simple_history.utils import update_change_reason

from app.models import Facility, Device, Municipality, PlatformAttribute, Platform, \
    FacilityMembership, DeviceConnection, CronJobExecution, CronJob, DeviceCalibrationModel, AlertScheme, \
    RockiotGlobalPreferenceModel, AqCategory, AqClassification
from app.system.decorators import action_form, device_event_form
from app.system.dockerops import DockerOps
from app.tasks import register_device, activate_device, deactivate_device, terminate_device, \
    send_device_metadata, send_platform_attributes, send_device_event
from app.widgets import MyPrettyJSONWidget

DEFAULT_CHOICE_DASH = []


class JSONFieldFilter(SimpleListFilter):

    @staticmethod
    def is_bool(x):
        return x in ("True", "true", True, "False", "false", False)

    @staticmethod
    def to_bool(x):
        return x in ("True", "true", True)

    model_json_field_name = None  # name of the json field column in the model
    json_data_property_name = None  # name of one attribute from json data

    def get_child_value_from_json_field_data(self, json_field_data):
        key_list = self.json_data_property_name.split('__')
        for key in key_list:
            if isinstance(json_field_data, dict):
                json_field_data = json_field_data.get(key, None)
        return json_field_data

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples.
        The first element in each tuple is the coded value for the option that will appear in the URL query.
        The 2nd element is the human-readable name for the option that will appear in the right sidebar.
        """
        if self.model_json_field_name is None:
            raise ImproperlyConfigured(
                f'Filter class {self.__class__.__name__} does not specify "model_json_field_name"')

        if self.json_data_property_name is None:
            raise ImproperlyConfigured(
                f'Filter class {self.__class__.__name__} does not specify "json_data_property_name"')

        field_value_set = set()

        for json_field_data in model_admin.model.objects.values_list(self.model_json_field_name, flat=True):
            field_data = self.get_child_value_from_json_field_data(json_field_data)
            if field_data is not None:
                field_value_set.add(field_data)

        return [(v, v) for v in field_value_set]

    @staticmethod
    def _retype_value(value):
        if value is None:
            return value
        if JSONFieldFilter.is_bool(value):
            value = JSONFieldFilter.to_bool(value)
            return value
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                value = str(value)
        finally:
            return value

    def value(self):
        return self._retype_value(super(JSONFieldFilter, self).value())

    def queryset(self, request, queryset):
        if self.value() is not None:
            json_field_query = {f'{self.model_json_field_name}__{self.json_data_property_name}': self.value()}
            return queryset.filter(**json_field_query)
        else:
            return queryset


class DeviceMetadataFirmwareFilter(JSONFieldFilter):
    model_json_field_name = 'metadata'
    json_data_property_name = 'device_fw'
    title = 'Device FW'
    parameter_name = 'metadata_device_fw'


class DeviceMetadataNo2ReadyFilter(JSONFieldFilter):
    model_json_field_name = 'metadata'
    json_data_property_name = 'no2_ready'
    title = 'NO2 Ready'
    parameter_name = 'metadata_no2_ready'


class DeviceMetadataNo2OnlineFilter(JSONFieldFilter):
    model_json_field_name = 'metadata'
    json_data_property_name = 'no2_online'
    title = 'NO2 Online'
    parameter_name = 'metadata_no2_online'


class DeviceMetadataSo2ReadyFilter(JSONFieldFilter):
    model_json_field_name = 'metadata'
    json_data_property_name = 'so2_ready'
    title = 'SO2 Ready'
    parameter_name = 'metadata_so2_ready'


class DeviceMetadataSo2OnlineFilter(JSONFieldFilter):
    model_json_field_name = 'metadata'
    json_data_property_name = 'so2_online'
    title = 'SO2 Online'
    parameter_name = 'metadata_so2_online'


class DeviceMetadataPmsOnlineFilter(JSONFieldFilter):
    model_json_field_name = 'metadata'
    json_data_property_name = 'pms_online'
    title = 'PMS Online'
    parameter_name = 'metadata_pms_online'


class FacilityFilter(SimpleListFilter):
    title = "Facility"
    parameter_name = "facility"

    def lookups(self, request, model_admin):
        facilities = set([c.facility for c in model_admin.model.objects.select_related('facility').all()])
        return [(c.id, c.name) for c in facilities]

    def queryset(self, request, queryset):
        if self.value():
            try:
                facility_id = int(self.value())
            except ValueError:
                return queryset.none()
            else:
                return queryset.filter(facility__id=facility_id)


class StateFilter(SimpleListFilter):
    title = "State"
    parameter_name = "state"

    def lookups(self, request, model_admin):
        return [('1', 'ONLINE'), ('2', 'OFFLINE')]

    def queryset(self, request, queryset):
        if self.value():
            try:
                state_id = int(self.value())
            except ValueError:
                return queryset.none()
            else:
                if state_id == 1:
                    return queryset.filter(connections__state='RUNNING')
                else:
                    return queryset.filter(
                        Q(connections__state='TERMINATED') | Q(connections__state='UNKNOWN') | Q(
                            connections__state__isnull=True)).exclude(connections__state='RUNNING') \
                        .distinct()


class DynamicLookupMixin(object):
    """
    a mixin to add dynamic callable attributes like 'book__author' which
    return a function that return the instance.book.author value
    """

    def __getattr__(self, attr):
        if '__' in attr and not attr.startswith('_') and not attr.endswith('_boolean') and not attr.endswith('_short_description'):

            def get_attr(parent, child):
                if type(parent) is dict:
                    return parent.get(child, "")
                else:
                    return getattr(parent, child)

            def dyn_lookup(instance):
                # traverse all __ lookups
                return reduce(lambda parent, child: get_attr(parent, child),
                              attr.split('__'),
                              instance)

            # get admin_order_field, boolean and short_description
            dyn_lookup.admin_order_field = attr
            dyn_lookup.boolean = getattr(self, '{}_boolean'.format(attr), False)
            attr_parent = attr.split('__')[0]
            if attr_parent.startswith("metadata"):
                attr_name = f"(M) {attr.split('__')[1]}"
            else:
                attr_name = attr
            dyn_lookup.short_description = getattr(
                self, '{}_short_description'.format(attr_name),
                attr_name.replace('_', ' ').capitalize())

            return dyn_lookup

        # not dynamic lookup, default behaviour
        return self.__getattribute__(attr)


class ActionMixin(object):

    def get_action_choices(self, request, default_choices=DEFAULT_CHOICE_DASH):
        choices = super().get_action_choices(request, default_choices)
        action_to_group = dict([
            (action_name, group_name)
            for group_name, params in self.action_groups_map.items()
            for action_name in params['actions']
        ])
        no_group = []
        groups = OrderedDict([
            (group_name, []) for group_name in self.action_groups_map.keys()
        ])
        for action_name, action_label in choices:
            group_name = action_to_group.get(action_name)
            if not group_name:
                no_group.append((action_name, action_label))
            else:
                groups[group_name].append((action_name, action_label))
        return no_group + [
            (self.action_groups_map[group_name]['label'], choices)
            for group_name, choices in groups.items() if choices
        ]


DeviceLogEntry = apps.get_model("app", "DeviceLogEntry")


class DeviceLogEntryResource(resources.ModelResource):
    object_action = Field(column_name="action")
    object_user = Field(column_name="user")
    object_change = Field(column_name="change")

    def dehydrate_object_action(self, entry):
        types = {'+': 'Created', '~': 'Changed', '-': 'Deleted'}
        return types.get(entry.history_type, 'Changed')

    def dehydrate_object_user(self, entry):
        if entry.history_user:
            return entry.history_user.username
        else:
            return ""

    def dehydrate_object_change(self, entry):
        new_record = entry
        old_record = new_record.prev_record
        if new_record and old_record:
            model_delta = new_record.diff_against(old_record, excluded_fields=["history_change"])
            return "%s" % [f"{c.field} ({c.old} -> {c.new})" for c in model_delta.changes]
        else:
            return None

    class Meta:
        model = DeviceLogEntry
        fields = ('device_id', 'object_action', 'history_date', 'object_user', 'object_change', 'history_change_reason')
        export_order = ('device_id', 'object_action', 'object_change', 'history_change_reason', 'object_user', 'history_date')


def get_form_field_overrides():
    return {
        models.CharField: {'widget': TextInput(attrs={'size': '40'})},
        models.EmailField: {'widget': TextInput(attrs={'size': '40'})},
        models.GenericIPAddressField: {'widget': TextInput(attrs={'size': '40'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
        models.JSONField: {'widget': MyPrettyJSONWidget(attrs={'initial': 'parsed', 'rows': 24, 'cols': 96})}
    }


# @admin.register(AlertScheme)
class AlertSchemeAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_display_links = ('name',)
    formfield_overrides = get_form_field_overrides()

    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {'fields': (
            'name',
            'scheme',
            'created_at',
            'updated_at')
        })
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class AlertSchemeInlineAdmin(admin.TabularInline):
    model = AlertScheme
    can_delete = False
    extra = 0
    show_change_link = True
    readonly_fields = ['created_at', 'updated_at']
    fields = ['name', 'created_at', 'updated_at']
    formfield_overrides = get_form_field_overrides()

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FacilityInlineAdmin(admin.TabularInline):
    model = Facility
    can_delete = False
    extra = 0
    show_change_link = False
    readonly_fields = ['created_at', 'updated_at']
    fields = ['code', 'name', 'type', 'address', 'municipality', 'updated_at']
    formfield_overrides = get_form_field_overrides()

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FacilityMembershipInline(admin.TabularInline):
    model = FacilityMembership
    can_delete = True
    extra = 0
    show_change_link = True
    fields = ['user', 'created_at']
    readonly_fields = ['created_at', ]
    formfield_overrides = get_form_field_overrides()


@admin.register(Municipality)
class MunicipalityAdmin(OSMGeoAdmin):
    map_template = 'admin/map-openlayers.html'
    default_zoom = 4
    list_display = ('name', 'code', 'created_at', 'updated_at')
    list_display_links = ('name',)
    list_filter = ('name', 'code')
    fieldsets = [
        (None, {'fields': ['name', 'code']}),
        ('Area', {'fields': ('area',)}),
    ]
    formfield_overrides = get_form_field_overrides()
    inlines = [FacilityInlineAdmin, ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class DeviceInlineAdmin(admin.TabularInline):
    model = Device
    can_delete = True
    extra = 0
    show_change_link = True
    readonly_fields = ['status', 'created_at', 'updated_at']
    fields = ['device_id', 'name', 'mode', 'status']
    formfield_overrides = get_form_field_overrides()

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Facility)
class FacilityAdmin(OSMGeoAdmin):
    map_template = 'admin/map-openlayers.html'
    default_zoom = 4
    list_display = ('code', 'name', 'type', 'address', 'municipality', 'updated_at')
    list_display_links = ('code', 'name',)
    list_filter = ('type',)
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {'fields': (
            'code', 'name',
            'address', 'email',
            'type', 'municipality',
            'description',
            'created_at', 'updated_at')}),
        ('Location', {'fields': ('location',)}),
    ]
    inlines = [DeviceInlineAdmin, FacilityMembershipInline, ]
    formfield_overrides = get_form_field_overrides()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class DeviceConnectionInlineAdmin(admin.TabularInline):
    model = DeviceConnection
    can_delete = False
    extra = 0
    show_change_link = False
    readonly_fields = ['name', 'user', 'client_id', 'msg_cnt', 'msg_rate',
                       'ip_address', 'faults', 'state', 'connected_at', 'terminated_at']
    fields = ['client_id', 'faults', 'msg_cnt', 'msg_rate', 'state', 'connected_at', 'terminated_at']
    formfield_overrides = get_form_field_overrides()

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        return True


class DeviceCalibrationModelInlineAdmin(admin.TabularInline):
    model = DeviceCalibrationModel
    can_delete = False
    extra = 0
    max_num = 1
    form = AlwaysChangedModelForm
    show_change_link = False
    readonly_fields = ['created_at', 'updated_at']
    fields = ['temperature', 'humidity', 'no2', 'so2', 'pm1', 'pm2_5', 'pm10']
    formfield_overrides = {models.CharField: {'widget': TextInput(attrs={'size': '7'})}}

    def has_add_permission(self, request, obj=None):
        return obj and obj.calibration_models and obj.calibration_models.count() <= 1

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DeviceLogEntry)
class DeviceLogEntryAdmin(ImportExportModelAdmin):

    model = DeviceLogEntry
    date_hierarchy = 'history_date'
    resource_class = DeviceLogEntryResource

    def history_change(self, obj):
        new_record = obj
        old_record = new_record.prev_record
        if new_record and old_record:
            model_delta = new_record.diff_against(old_record, excluded_fields=["history_change"])
            return "%s" % [f"{c.field} ({c.old} -> {c.new})" for c in model_delta.changes]
        else:
            return "[]"

    list_display = ('device_id', 'history_date', 'history_user', 'history_type', 'history_change_reason')
    list_display_links = ('device_id', 'history_date',)
    list_filter = ('device_id', 'history_type', 'history_user')
    readonly_fields = ['device_id', 'history_type', 'history_date', 'history_user', "history_change"]
    formfield_overrides = get_form_field_overrides()
    fieldsets = [
        (None, {'fields': (
            'device_id',
            'history_date',
            'history_user',
            'history_type'
        )}),
        ('Changes', {'fields': ['history_change']}),
        ('Reason', {'fields': ['history_change_reason']}),
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def get_export_filename(self, request, queryset, file_format):
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"devices-changelog-{date_str}.{file_format.get_extension()}"


class DeviceChangeComment(forms.Form):
    title = 'Please add comment to describe change'
    comment = forms.CharField(max_length=128)


class DeviceSendEventForm(forms.Form):
    title = 'Select an event to send to device'
    MY_CHOICES = (
        ('zero_sensors', 'Zero Sensors'),
        ('zero_so2', 'Zero So2 Sensor'),
        ('zero_no2', 'Zero No2 Sensor'),
        ('erase_wifi_credentials', 'Erase WiFi Credentials'),
        ('reboot_device', 'Reboot Device'),
        ('erase_zeroing_data', 'Erase Zeroing Data'),
        ('identify_device', 'Identify Device'),
    )
    event = forms.ChoiceField(choices=MY_CHOICES)


@admin.register(Device)
class DeviceAdmin(ActionMixin, DynamicLookupMixin, OSMGeoAdmin, SimpleHistoryAdmin):

    map_template = 'admin/map-openlayers.html'
    default_zoom = 4

    actions = ['register', 'activate', 'deactivate', 'terminate', 'start_container', 'stop_container', 'mode_default', 'mode_calibration', 'mode_production', 'send_event_to_device']

    action_groups_map = OrderedDict({
        'Status': {
            'label': 'Device status',
            'actions': ('register', 'activate', 'deactivate', 'terminate')
        },
        'Mode': {
            'label': 'Device mode',
            'actions': ('mode_default', 'mode_calibration', 'mode_production')
        },
        'Actions': {
            'label': 'Device actions',
            'actions': ('send_event_to_device', )
        },
        'Demo': {
            'label': 'Device demo',
            'actions': ('start_container', 'stop_container')
        },
    })

    @action_form(DeviceChangeComment, initial_value="Status changed to: REGISTERED")
    def register(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            register_device.apply_async((device.device_id,))
            device.status = Device.REGISTERED
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Status changed to: ACTIVATED")
    def activate(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            activate_device.apply_async((device.device_id,))
            device.status = Device.ACTIVATED
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Status changed to: DEACTIVATED")
    def deactivate(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            deactivate_device.apply_async((device.device_id,))
            device.status = Device.DEACTIVATED
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Status changed to: TERMINATED")
    def terminate(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            terminate_device.apply_async((device.device_id,))
            device.status = Device.TERMINATED
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Mode changed to: DEFAULT")
    def mode_default(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset.exclude(mode=Device.DEFAULT):
            device.mode = Device.DEFAULT
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Mode changed to: CALIBRATION")
    def mode_calibration(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset.exclude(mode=Device.CALIBRATION):
            device.mode = Device.CALIBRATION
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Mode changed to: PRODUCTION")
    def mode_production(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset.exclude(mode=Device.PRODUCTION):
            device.mode = Device.PRODUCTION
            device.save()
            update_change_reason(device, comment)

    @device_event_form(DeviceSendEventForm, initial_value="Event sent to Device")
    def send_event_to_device(self, request, queryset, form):
        event_type = form.cleaned_data['event']
        for device in queryset.filter(status=Device.ACTIVATED):
            send_device_event.apply_async((device.device_id, event_type))
            device.event_sent_at = datetime.now()  # TODO: check millis
            device.save()
            update_change_reason(device, f"Sent {event_type}")

    def start_container(self, request, queryset):
        success = False
        for device in queryset:
            success = DockerOps.start_demo_container(device)
            break
        if success:
            messages.add_message(request, messages.INFO, 'Device demo will soon be started. Refresh page for updates.')
        else:
            messages.add_message(request, messages.ERROR, 'Failed starting Device demo. System error.')

    def stop_container(self, request, queryset):
        success = False
        for device in queryset:
            success = DockerOps.stop_demo_container(device)
            break
        if success:
            messages.add_message(request, messages.INFO, 'Device demo will soon be stopped. Refresh page for updates.')
        else:
            messages.add_message(request, messages.ERROR, 'Failed stopping Device demo. System error.')

    def municipality(self, obj):
        return obj.municipality_name()

    def state(self, obj):
        connection = obj.connections.first()
        s = "UNKNOWN" if not connection else connection.state
        colors = {
            'RUNNING': '#44B78B',
            'TERMINATED': '#A41515',
            'UNKNOWN': '#0C4B33',
        }
        names = {
            'RUNNING': 'ONLINE',
            'TERMINATED': 'OFFLINE',
            'UNKNOWN': 'OFFLINE',
        }
        return format_html('<b style="color:{};">{}</b>', colors[s], names[s], )

    def activation_status(self, obj):
        colors = {
            'NEW': '#0C4B33',
            'REGISTERED': '#0C4B33',
            'ACTIVATED': '#44B78B',
            'DEACTIVATED': '#A41515',
            'TERMINATED': '#A41515',
        }
        return format_html('<b style="color:{};">{}</b>', colors[obj.status], obj.status, )

    state.short_description = 'State'
    activation_status.short_description = 'Status'
    register.short_description = "Register"
    activate.short_description = "Activate"
    deactivate.short_description = "Deactivate"
    terminate.short_description = "Terminate"
    mode_default.short_description = "Reset"
    mode_calibration.short_description = "Calibrate"
    mode_production.short_description = "Production"
    start_container.short_description = "Start"
    stop_container.short_description = "Stop"
    send_event_to_device.short_description = "Send Event"

    def get_row_actions(self, obj):
        row_actions = []
        row_actions += super(DeviceAdmin, self).get_row_actions(obj)
        return row_actions

    def get_list_display(self, request):
        pref = request.user.preferences['device__table_columns']
        if pref:
            list_display = pref.split(', ')
        else:
            list_display = ('device_id', 'name', 'facility', 'municipality', 'mode', 'activation_status', 'state')
        return list_display

    def get_list_display_links(self, request, list_display):
        pref = request.user.preferences['device__table_columns_links']
        if pref:
            return pref.split(', ')
        else:
            return super().get_list_display_links(request, list_display)

    def get_list_filter(self, request):
        optional_field_sets = {
            'facility': FacilityFilter,
            'state': StateFilter,
            'device_fw': DeviceMetadataFirmwareFilter,
            'no2_ready': DeviceMetadataNo2ReadyFilter,
            'so2_ready': DeviceMetadataSo2ReadyFilter,
            'no2_online': DeviceMetadataNo2OnlineFilter,
            'so2_online': DeviceMetadataSo2OnlineFilter,
            'pms_online': DeviceMetadataPmsOnlineFilter
        }
        list_filter = []
        pref = request.user.preferences['device__table_filter']
        if pref:
            for s in pref.split(', '):
                filtr = optional_field_sets.get(s.strip(), None)
                if filtr is not None:
                    list_filter.append(filtr)
                else:
                    list_filter.append(s.strip())
        else:
            list_filter = ('status', 'mode')
        return list_filter

    history_list_display = ["status"]

    def get_queryset(self, request):
        qs = super(DeviceAdmin, self).get_queryset(request)
        return qs.prefetch_related('connections')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['device_id', 'status', 'created_at', 'updated_at', 'state']
        else:
            return ['status', 'created_at', 'updated_at', 'state']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {'fields': (
                'device_id',
                ('name', 'mode'),
                ('description', 'facility')
            )})
        ]
        pref_location_opened = request.user.preferences['device__form_location_opened']
        optional_field_sets = {
            'Location': ('Location', {'fields': ('location',), 'classes': ['' if pref_location_opened else 'collapse']}),
            'Metadata': ('Metadata', {'fields': ('metadata',)}),
            'Confidential': ('Confidential', {'fields': ('device_pass',), 'classes': ['collapse']})
        }
        pref = request.user.preferences['device__form_sections']
        if pref:
            for s in pref.split(', '):
                fieldsets.append(optional_field_sets.get(s.strip()))
        else:
            fieldsets.append(optional_field_sets.get('Location'))
            fieldsets.append(optional_field_sets.get('Metadata'))
            fieldsets.append(optional_field_sets.get('Confidential'))
        return fieldsets

    inlines = [DeviceCalibrationModelInlineAdmin, DeviceConnectionInlineAdmin]
    formfield_overrides = get_form_field_overrides()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions

    def save_model(self, request, obj, form, change):
        metadata_changed = False
        if change:
            reason = ""
            if 'mode' in form.changed_data:
                initial = form.get_initial_for_field(form.fields['mode'], 'mode')
                if obj.mode != initial:
                    reason = f"Mode changed to: {form.cleaned_data['mode']}"
            if 'facility' in form.changed_data:
                initial = form.get_initial_for_field(form.fields['facility'], 'facility')
                if obj.facility != initial:
                    if len(reason) > 0:
                        reason += "\n"
                    reason += f"Location changed to: {form.cleaned_data['facility']}"
            if 'metadata' in form.changed_data:
                initial = form.get_initial_for_field(form.fields['metadata'], 'metadata')
                if obj.metadata != initial:
                    if len(reason) > 0:
                        reason += "\n"
                    reason += f"Metadata changed"
                    metadata_changed = True
            if len(reason) == 0:
                reason = "Values changed"
        super(DeviceAdmin, self).save_model(request, obj, form, change)
        if change:
            update_change_reason(obj, reason)
            if metadata_changed:
                send_device_metadata.apply_async((obj.device_id,))


class CronJobExecutionAdmin(admin.TabularInline):
    model = CronJobExecution
    can_delete = False
    extra = 0
    show_change_link = False
    formfield_overrides = get_form_field_overrides()
    fields = ['runid', 'job_pid', 'status', 'start_time', 'end_time']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CronJobList(admin.TabularInline):
    model = CronJob
    can_delete = False
    extra = 0
    show_change_link = True
    formfield_overrides = get_form_field_overrides()
    fields = ['jobid', 'jobname', 'schedule', 'command']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CronJob)
class CronJobAdmin(ModelAdmin):
    list_display = ('jobid', 'jobname', 'schedule')
    list_display_links = ('jobid', 'jobname',)
    inlines = [CronJobExecutionAdmin, ]
    formfield_overrides = get_form_field_overrides()

    readonly_fields = ['jobid', 'jobname']
    fieldsets = [
        (None, {'fields': (
            'jobid',
            'jobname',
            'schedule',
            'command')
        })
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PlatformAttributeAdminInline(admin.TabularInline):
    model = PlatformAttribute
    can_delete = True
    extra = 0
    show_change_link = True
    readonly_fields = ['created_at', 'updated_at']
    fields = ['name', 'value']
    formfield_overrides = get_form_field_overrides()


@admin.register(Platform)
class PlatformAdmin(ModelAdmin):
    list_display = ('name', 'description')
    list_display_links = ('name',)
    fieldsets = [
        (None, {'fields': ['name', 'description']}),
    ]
    inlines = [PlatformAttributeAdminInline, ]
    formfield_overrides = get_form_field_overrides()

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        super(PlatformAdmin, self).save_model(request, obj, form, change)
        if change:
            send_platform_attributes.apply_async()


admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(GroupResult)
admin.site.unregister(TaskResult)


class RockiotTaskResultAdmin(TaskResultAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TaskResult, RockiotTaskResultAdmin)

# admin.site.index_template = 'admin/rockiot_index.html'

admin.site.unregister(GlobalPreferenceModel)
admin.site.register(RockiotGlobalPreferenceModel, GlobalPreferenceAdmin)


class RockiotUserPreferenceAdmin(UserPreferenceAdmin):
    search_fields = ['instance__username'] + DynamicPreferenceAdmin.search_fields
    form = UserSinglePreferenceForm
    list_display = ('verbose_name', 'name', 'help_text', 'raw_value', 'default_value')
    list_display_links = ('verbose_name', 'name')
    changelist_form = UserSinglePreferenceForm

    def get_queryset(self, request, *args, **kwargs):
        getattr(request.user, preferences_settings.MANAGER_ATTRIBUTE).all()
        return super(UserPreferenceAdmin, self).get_queryset(
            request, *args, **kwargs)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.unregister(UserPreferenceModel)
admin.site.register(UserPreferenceModel, RockiotUserPreferenceAdmin)


class AqCategoryAdmin(admin.TabularInline):
    model = AqCategory
    list_display = ('name', 'classification', 'pollutant', 'timeframe', 'lower_limit', 'upper_limit')
    formfield_overrides = get_form_field_overrides()
    extra = 0
    show_change_link = True
    can_delete = True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(AqClassification)
class AqClassificationAdmin(ModelAdmin):
    list_display = ('name', 'description')
    formfield_overrides = get_form_field_overrides()
    inlines = [AqCategoryAdmin]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

