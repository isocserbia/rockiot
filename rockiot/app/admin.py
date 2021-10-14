from collections import OrderedDict
from datetime import datetime

from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.gis.admin import OSMGeoAdmin
from django.db import models
from django.forms import TextInput, Textarea, ModelForm
from django.utils.html import format_html
from django_celery_beat.models import SolarSchedule, ClockedSchedule
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import GroupResult, TaskResult
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from prettyjson import PrettyJSONWidget
from simple_history.admin import SimpleHistoryAdmin
from simple_history.utils import update_change_reason

from app.models import Facility, Device, Municipality, PlatformAttribute, Platform, \
    FacilityMembership, DeviceConnection, CronJobExecution, CronJob, DeviceCalibrationModel
from app.system.decorators import action_form
from app.system.dockerops import DockerOps
from app.tasks import register_device, activate_device, deactivate_device, terminate_device, zero_config, \
    send_device_metadata, send_platform_attributes, erase_wifi_credentials

DEFAULT_CHOICE_DASH = []


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
        models.JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed', 'rows': 24, 'cols': 96})}
    }


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
    list_display = ('name', 'code', 'created_at', 'updated_at')
    list_display_links = ('name',)
    list_filter = ('name', 'code')
    fieldsets = [
        (None, {'fields': ['name', 'code', 'area']}),
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
    list_display = ('code', 'name', 'type', 'address', 'municipality', 'updated_at')
    list_display_links = ('code', 'name',)
    list_filter = ('type',)
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {'fields': (
            'code', 'name',
            'address', 'email',
            'type', 'municipality',
            'location',
            'description',
            'created_at', 'updated_at')})
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


@admin.register(Device)
class DeviceAdmin(ActionMixin, OSMGeoAdmin, SimpleHistoryAdmin):

    actions = ['register', 'activate', 'deactivate', 'terminate', 'start_container', 'stop_container', 'mode_default', 'mode_calibration', 'mode_production', 'zero_config', 'erase_wifi_credentials']

    action_groups_map = OrderedDict({
        'Status': {
            'label': 'Device status',
            'actions': ('register', 'activate', 'deactivate', 'terminate')
        },
        'Mode': {
            'label': 'Device mode',
            'actions': ('mode_default', 'mode_calibration', 'mode_production')
        },
        'Config': {
            'label': 'Device config',
            'actions': ('zero_config', 'erase_wifi_credentials')
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

    @action_form(DeviceChangeComment, initial_value="Zero config sent")
    def zero_config(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset.filter(status=Device.ACTIVATED):
            zero_config.apply_async((device.device_id,))
            device.zero_config_at = datetime.now()  # TODO: check millis
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Erase Wifi credentials sent")
    def erase_wifi_credentials(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset.filter(status=Device.ACTIVATED):
            erase_wifi_credentials.apply_async((device.device_id,))
            device.erase_wifi_credentials_at = datetime.now()  # TODO: check millis
            device.save()
            update_change_reason(device, comment)

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
        connection = DeviceConnection.objects.filter(device=obj).first()
        s = "UNKNOWN" if not connection else connection.state
        colors = {
            'RUNNING': '#44B78B',
            'TERMINATED': '#A41515',
            'UNKNOWN': '#0C4B33',
        }
        return format_html('<b style="color:{};">{}</b>', colors[s], s, )

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
    zero_config.short_description = "Zero Config"
    erase_wifi_credentials.short_description = "Erase Wifi Credentials"
    start_container.short_description = "Start"
    stop_container.short_description = "Stop"

    def get_row_actions(self, obj):
        row_actions = []
        row_actions += super(DeviceAdmin, self).get_row_actions(obj)
        return row_actions

    list_display = ('device_id', 'name', 'facility', 'municipality', 'mode', 'activation_status', 'state')
    list_display_links = ('device_id', 'name')
    list_filter = ('status', 'mode')
    history_list_display = ["status"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['device_id', 'status', 'created_at', 'updated_at', 'state']
        else:
            return ['status', 'created_at', 'updated_at', 'state']

    fieldsets = [
        (None, {'fields': (
            'device_id',
            ('name', 'mode'),
            ('description', 'facility')
        )}),
        ('Location', {'fields': ('location',)}),
        ('Metadata', {'fields': ('metadata',)}),
        ('Confidential', {'fields': ('device_pass',), 'classes': ['collapse']})
    ]

    inlines = [DeviceCalibrationModelInlineAdmin, DeviceConnectionInlineAdmin, ]
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


class MyTaskResultAdmin(TaskResultAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TaskResult, MyTaskResultAdmin)

# admin.site.index_template = 'admin/rockiot_index.html'
