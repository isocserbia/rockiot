from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.gis.admin import OSMGeoAdmin
from django.db import models
from django.forms import TextInput, Textarea
from django.utils.html import format_html
from django_celery_beat.models import SolarSchedule, ClockedSchedule
from django_celery_results.models import GroupResult

from app.models import Facility, Device, Municipality, PlatformAttribute, Platform, \
    FacilityMembership, DeviceConnection, CronJobExecution, CronJob
from app.system.dockerops import DockerOps
from app.tasks import register_device, activate_device, deactivate_device, terminate_device


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
    fields = ['device_id', 'name', 'type', 'profile', 'status']
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


@admin.register(Device)
class DeviceAdmin(OSMGeoAdmin):

    actions = ['register', 'activate', 'deactivate', 'terminate', 'start_container', 'stop_container']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # register_device.apply_async((obj.device_id,))

    def register(self, request, queryset):
        for device in queryset:
            register_device.apply_async((device.device_id,))
            device.status = Device.REGISTERED
            device.save()

    def activate(self, request, queryset):
        for device in queryset:
            activate_device.apply_async((device.device_id,))
            device.status = Device.ACTIVATED
            device.save()

    def deactivate(self, request, queryset):
        for device in queryset:
            deactivate_device.apply_async((device.device_id,))
            device.status = Device.DEACTIVATED
            device.save()

    def terminate(self, request, queryset):
        for device in queryset:
            terminate_device.apply_async((device.device_id,))
            device.status = Device.TERMINATED
            device.save()

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

    def state(self, obj):
        connection = DeviceConnection.objects.filter(device=obj).first()
        s = "UNKNOWN" if not connection else connection.state
        colors = {
            'RUNNING': '#44B78B',
            'TERMINATED': '#A41515',
            'UNKNOWN': '#0C4B33',
        }
        return format_html('<b style="color:{};">{}</b>', colors[s], s,)

    def activation_status(self, obj):
        colors = {
            'NEW': '#0C4B33',
            'REGISTERED': '#0C4B33',
            'ACTIVATED': '#44B78B',
            'DEACTIVATED': '#A41515',
            'TERMINATED': '#A41515',
        }
        return format_html('<b style="color:{};">{}</b>', colors[obj.status], obj.status,)

    state.admin_order_field = 'unknown'
    activation_status.admin_order_field = 'unknown'
    register.short_description = "Register devices"
    activate.short_description = "Activate devices"
    deactivate.short_description = "Deactivate devices"
    terminate.short_description = "Terminate devices"
    start_container.short_description = "Start devices (demo)"
    stop_container.short_description = "Stop devices (demo)"

    def get_row_actions(self, obj):
        row_actions = []
        row_actions += super(DeviceAdmin, self).get_row_actions(obj)
        return row_actions

    list_display = ('device_id', 'name', 'type', 'facility', 'activation_status', 'state')
    list_display_links = ('device_id', 'name')
    list_filter = ('status', 'type')
    readonly_fields = ['status', 'created_at', 'updated_at', 'state']
    fieldsets = [
        (None, {'fields': (
            ('device_id', 'type'),
            ('name', 'profile'),
            ('description', 'facility')
        )}),
        ('Location', {'fields': ('location',)}),
        ('Confidential', {'fields': ('device_pass',), 'classes': ['collapse']}),
    ]

    inlines = [DeviceConnectionInlineAdmin, ]
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
