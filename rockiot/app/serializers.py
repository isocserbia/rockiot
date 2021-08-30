import rest_framework
from rest_framework.serializers import CharField
from rest_framework_gis import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.models import *


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['groups'] = ", ".join([g.name for g in user.groups.all()])
        return token


class MunicipalityModelSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        pass

    class Meta:
        model = Municipality
        exclude = ["id", "area"]


class DeviceModelSerializer(serializers.ModelSerializer):
    lon = rest_framework.serializers.ReadOnlyField()
    lat = rest_framework.serializers.ReadOnlyField()

    class Meta:
        model = Device
        exclude = ["id", "device_pass", "device_key", "facility", "location"]


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


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ["time", "temperature", "humidity", "no2", "so2", "pm10", "pm25"]


class SensorsDataRollupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorsDataRollup1h
        fields = ["time", "temperature", "humidity", "no2", "so2", "pm10", "pm25"]


class SensorsDataRollupWithDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorsDataRollup1h
        fields = ["device_id", "time", "temperature", "humidity", "no2", "so2", "pm10", "pm25"]


class SensorDataLastValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDataLastValues
        fields = ["device_id", "time", "temperature", "humidity", "no2", "so2", "pm10", "pm25"]


class CronJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronJob
