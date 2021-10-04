from datetime import timezone, time

import rest_framework
from rest_framework.serializers import CharField, SerializerMethodField, DateTimeField
from rest_framework_gis import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.models import *
from django.apps import apps


class DateTimeTzAwareField(DateTimeField):

    def to_native(self, value):
        value = timezone.fromutc(value)
        native = super(DateTimeTzAwareField, self).to_native(value)
        return native


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['groups'] = ", ".join([g.name for g in user.groups.all()])
        return token


class MunicipalityModelSerializer(serializers.ModelSerializer):
    # dtz = pytz.timezone('Europe/Belgrade')
    # created_at = DateTimeTzAwareField(default_timezone=dtz, format='%Y-%m-%d %H:%M')
    # updated_at = DateTimeTzAwareField(default_timezone=dtz, format='%Y-%m-%d %H:%M')

    def validate(self, attrs):
        pass

    class Meta:
        model = Municipality
        exclude = ["id", "area"]


class DeviceModelSerializer(serializers.ModelSerializer):
    lon = rest_framework.serializers.ReadOnlyField()
    lat = rest_framework.serializers.ReadOnlyField()
    school_code = CharField(source='facility.code')
    last_active_at = SerializerMethodField()

    def get_last_active_at(self, obj):
        try:
            last_entry = SensorDataRaw.objects.filter(device_id=obj.device_id).first()
            if last_entry and last_entry is not None:
                return last_entry.time.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                return None
        except Exception as ex:
            logger.error("error occurred during fetch of last active at", ex)
            return 0.0

    class Meta:
        model = Device
        fields = ["name", "device_id", "school_code", "lon", "lat", "status", "mode",
                  "last_active_at", "created_at", "updated_at"]


DeviceLogEntry = apps.get_model("app", "DeviceLogEntry")


class DeviceLogEntrySerializer(serializers.ModelSerializer):
    # dtz = pytz.timezone('Europe/Belgrade')
    action = SerializerMethodField()
    change = SerializerMethodField()
    user = SerializerMethodField()
    # history_date = DateTimeTzAwareField(default_timezone=dtz, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = DeviceLogEntry
        fields = ['device_id', 'action', 'change', 'history_change_reason', 'user', 'history_date']

    def get_action(self, obj):
        try:
            types = {'+': 'Created', '~': 'Changed', '-': 'Deleted'}
            return types.get(obj.history_type, 'Changed')
        except TypeError:
            return "/"

    def get_change(self, obj):
        try:
            new_record = obj
            old_record = new_record.prev_record
            if new_record and old_record:
                model_delta = new_record.diff_against(old_record, excluded_fields=["metadata", "history_change"])
                return "%s" % [f"{c.field} ({c.old} -> {c.new})" for c in model_delta.changes]
            else:
                return None
        except TypeError:
            return "/"

    def get_user(self, obj):
        try:
            if obj.history_user:
                return obj.history_user.username
            else:
                return "/"
        except TypeError:
            return "/"


class FacilityMembershipSerializer(serializers.ModelSerializer):
    user_email = CharField(source='user.email')

    class Meta:
        model = FacilityMembership
        fields = ["id", "user_email", "created_at"]


class FacilityModelSerializer(serializers.ModelSerializer):
    devices = DeviceModelSerializer(many=True, read_only=True)
    municipality = MunicipalityModelSerializer(many=False, read_only=True)
    memberships = FacilityMembershipSerializer(many=True, read_only=True)
    lon = rest_framework.serializers.ReadOnlyField()
    lat = rest_framework.serializers.ReadOnlyField()

    class Meta:
        model = Facility
        fields = ['name', 'type', 'email', 'description', 'address', 'lon', 'lat',
                  'municipality', 'location', 'created_at', 'updated_at', 'devices', 'memberships']


class FacilitySerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Facility
        fields = ("id", "name")
        geo_field = "location"


class SensorDataRawSerializer(serializers.ModelSerializer):
    temperature = SerializerMethodField()
    humidity = SerializerMethodField()
    no2 = SerializerMethodField()
    so2 = SerializerMethodField()
    pm1 = SerializerMethodField()
    pm10 = SerializerMethodField()
    pm2_5 = SerializerMethodField()

    class Meta:
        model = SensorDataRaw
        fields = ["time", "temperature", "humidity", "no2", "so2", "pm1", "pm10", "pm2_5"]

    def get_temperature(self, obj):
        try:
            return obj.data['temperature']
        except TypeError:
            return 0.0

    def get_humidity(self, obj):
        try:
            return obj.data['humidity']
        except TypeError:
            return 0.0

    def get_no2(self, obj):
        try:
            return obj.data['no2']
        except TypeError:
            return 0.0

    def get_so2(self, obj):
        try:
            return obj.data['so2']
        except TypeError:
            return 0.0

    def get_pm1(self, obj):
        try:
            return obj.data['pm1']
        except TypeError:
            return 0.0

    def get_pm10(self, obj):
        try:
            return obj.data['pm10']
        except TypeError:
            return 0.0

    def get_pm2_5(self, obj):
        try:
            return obj.data['pm2_5']
        except TypeError:
            return 0.0


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ["time", "temperature", "humidity", "no2", "so2", "pm1", "pm10", "pm2_5"]


class SensorsDataRollupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorsDataRollup1h
        fields = ["time", "temperature", "humidity", "no2", "so2", "pm1", "pm10", "pm2_5"]


class SensorsDataRollupWithDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorsDataRollup1h
        fields = ["device_id", "time", "temperature", "humidity", "no2", "so2", "pm1", "pm10", "pm2_5"]


class SensorDataLastValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDataLastValues
        fields = ["device_id", "time", "temperature", "humidity", "no2", "so2", "pm1", "pm10", "pm2_5"]


class CronJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronJob
