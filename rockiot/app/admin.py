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
from import_export.admin import ExportActionModelAdmin
from import_export.fields import Field
from simple_history.admin import SimpleHistoryAdmin
from simple_history.utils import update_change_reason

from app.models import Facility, Device, Municipality, PlatformAttribute, Platform, \
    FacilityMembership, DeviceConnection, CronJobExecution, CronJob, DeviceCalibrationModel
from app.system.decorators import action_form
from app.system.dockerops import DockerOps
from app.tasks import register_device, activate_device, deactivate_device, terminate_device

DeviceLogEntry = apps.get_model("app", "DeviceLogEntry")


class DeviceLogEntryResource(resources.ModelResource):
    object_action = Field(column_name="action")
    object_user = Field(column_name="user")
    object_change = Field(column_name="change")

    def dehydrate_object_action(self, entry):
        types = {'+': 'Created', '~': 'Changed', '-': 'Deleted'}
        return types.get(entry.history_type, 'Changed')

    def dehydrate_object_user(self, entry):
        return entry.history_user.username

    def dehydrate_object_change(self, entry):
        new_record = entry
        old_record = new_record.prev_record
        if new_record and old_record:
            model_delta = new_record.diff_against(old_record, excluded_fields=["metadata", "history_change"])
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
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})}
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
class DeviceLogEntryAdmin(ExportActionModelAdmin):
    model = DeviceLogEntry

    date_hierarchy = 'history_date'
    resource_class = DeviceLogEntryResource

    def history_change(self, obj):
        new_record = obj
        old_record = new_record.prev_record
        if new_record and old_record:
            model_delta = new_record.diff_against(old_record, excluded_fields=["metadata", "history_change"])
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


class DeviceChangeComment(forms.Form):
    title = 'Please add comment to describe change'
    comment = forms.CharField(max_length=40)


@admin.register(Device)
class DeviceAdmin(OSMGeoAdmin, SimpleHistoryAdmin):
    actions = ['register', 'activate', 'deactivate', 'terminate', 'start_container', 'stop_container']

    @action_form(DeviceChangeComment, initial_value="Device registered")
    def register(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            register_device.apply_async((device.device_id,))
            device.status = Device.REGISTERED
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Device activated")
    def activate(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            activate_device.apply_async((device.device_id,))
            device.status = Device.ACTIVATED
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Device deactivated")
    def deactivate(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            deactivate_device.apply_async((device.device_id,))
            device.status = Device.DEACTIVATED
            device.save()
            update_change_reason(device, comment)

    @action_form(DeviceChangeComment, initial_value="Device terminated")
    def terminate(self, request, queryset, form):
        comment = form.cleaned_data['comment']
        for device in queryset:
            terminate_device.apply_async((device.device_id,))
            device.status = Device.TERMINATED
            device.save()
            update_change_reason(device, comment)

    def start_container(self, request, queryset):
        for device in queryset:
            DockerOps.start_demo_container(device)
            # only_one
            break
        messages.add_message(request, messages.INFO, 'Device demo will soon be started. Refresh page for updates.')

    def stop_container(self, request, queryset):
        for device in queryset:
            DockerOps.stop_demo_container(device)
            # only_one
            break
        messages.add_message(request, messages.INFO, 'Device demo will soon be stopped. Refresh page for updates.')

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
    start_container.short_description = "Start (demo)"
    stop_container.short_description = "Stop (demo)"

    def get_row_actions(self, obj):
        row_actions = []
        row_actions += super(DeviceAdmin, self).get_row_actions(obj)
        return row_actions

    list_display = ('device_id', 'name', 'facility', 'municipality', 'mode', 'activation_status', 'state')
    list_display_links = ('device_id', 'name')
    list_filter = ('status', 'mode')
    readonly_fields = ['status', 'created_at', 'updated_at', 'state']
    history_list_display = ["status"]

    fieldsets = [
        (None, {'fields': (
            'device_id',
            ('name', 'mode'),
            ('description', 'facility')
        )}),
        ('Location', {'fields': ('location',)}),
        ('Metadata', {'fields': ('metadata',), 'classes': ['collapse']}),
        ('Confidential', {'fields': ('device_pass',), 'classes': ['collapse']})
    ]

    inlines = [DeviceCalibrationModelInlineAdmin, DeviceConnectionInlineAdmin, ]
    formfield_overrides = get_form_field_overrides()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


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


class AttributesAdminInline(admin.TabularInline):
    model = PlatformAttribute
    can_delete = True
    extra = 0
    show_change_link = True
    readonly_fields = ['created_at', 'updated_at']
    fields = ['name', 'value']
    formfield_overrides = get_form_field_overrides()


@admin.register(Platform)
class PlatformAdmin(ModelAdmin):
    change_list_template = "admin/platform_changelist.html"
    list_display = ('name', 'description')
    list_display_links = ('name',)
    fieldsets = [
        (None, {'fields': ['name', 'description']}),
    ]
    inlines = [AttributesAdminInline, ]
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
