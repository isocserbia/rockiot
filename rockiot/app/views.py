"""Markers view."""
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase

from app.models import Facility, SensorData, SensorDataLastValues, Device, Municipality, \
    SensorsDataRollupAbstract
from app.serializers import FacilityModelSerializer, MyTokenObtainPairSerializer, SensorDataSerializer, \
    SensorDataLastValuesSerializer, DeviceModelSerializer, \
    SensorsDataRollupSerializer, MunicipalityModelSerializer, SensorsDataRollupWithDeviceSerializer


class EducationFacilityMapView(TemplateView):
    template_name = "map.html"


class DevicesList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of Device entities",
                         operation_summary="Gets all Devices",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Device.objects.all()
    serializer_class = DeviceModelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class MunicipalityView(generics.RetrieveAPIView):
    @swagger_auto_schema(operation_description="Retrieve single Municipality entity",
                         operation_summary="Gets Municipality by code",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        code = self.kwargs['code']
        return get_object_or_404(Municipality, code)

    serializer_class = MunicipalityModelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class MunicipalityList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of all Municipality entities",
                         operation_summary="Gets all Municipalities",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Municipality.objects.all()
    serializer_class = MunicipalityModelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class FacilityView(generics.RetrieveAPIView):
    @swagger_auto_schema(operation_description="Retrieve single Facility entity",
                         operation_summary="Gets Facility by code",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        code = self.kwargs['code']
        return get_object_or_404(Facility, code)

    serializer_class = FacilityModelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class FacilityList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of all Facility entities",
                         operation_summary="Gets all Facilities",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Facility.objects.all()
    serializer_class = FacilityModelSerializer
    permission_classes = [IsAuthenticated, ]


from_date_param = openapi.Parameter('from_date', openapi.IN_QUERY,
                                    description="Starting from date",
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME)

until_date_param = openapi.Parameter('until_date', openapi.IN_QUERY,
                                     description="Until date",
                                     type=openapi.TYPE_STRING,
                                     format=openapi.FORMAT_DATETIME)


class SensorDataList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve raw sensor data reading",
                         operation_summary="Gets Raw Sensor data for single Device",
                         tags=['report'],
                         manual_parameters=[from_date_param, until_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        did = self.kwargs['device_id']
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        return SensorData.objects.filter(device_id=did, time__date__gt=from_date, time__date__lt=until_date)

    serializer_class = SensorDataSerializer
    permission_classes = [IsAuthenticated, ]  # UserDevicePermission


interval_param = openapi.Parameter('interval', openapi.IN_QUERY,
                                   description="interval ('5m','1h','4h','24h')",
                                   type=openapi.TYPE_STRING)


class DeviceSensorsSummary(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of aggregated Sensor data for Device and time Interval",
                         operation_summary="Gets aggregated Sensor data for Device",
                         tags=['report'],
                         manual_parameters=[interval_param, from_date_param, until_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        device_id = self.kwargs['device_id']
        interval = self.request.query_params.get('interval')
        model_cls = SensorsDataRollupAbstract.get_class_for_interval(interval)
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        return model_cls.objects.filter(device_id=device_id, time__date__gt=from_date, time__date__lt=until_date)

    serializer_class = SensorsDataRollupSerializer
    permission_classes = [AllowAny, ]


class FacilitySensorsSummary(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of aggregated Sensor data for Facility and time Interval",
                         operation_summary="Gets aggregated Sensor data for Facility",
                         tags=['report'],
                         manual_parameters=[interval_param, from_date_param, until_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        code = self.kwargs['code']
        interval = self.request.query_params.get('interval')
        model_cls = SensorsDataRollupAbstract.get_class_for_interval(interval)
        ids = list([d.device_id for d in Device.objects.filter(educational_facility__code=code)])
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        return model_cls.objects.filter(device_id__in=ids, time__date__gt=from_date, time__date__lt=until_date)

    serializer_class = SensorsDataRollupWithDeviceSerializer
    permission_classes = [AllowAny, ]


class MunicipalitySensorsSummary(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of aggregated Sensor data for Municipality and time "
                                               "Interval",
                         operation_summary="Gets aggregated Sensor data for Municipality",
                         tags=['report'],
                         manual_parameters=[interval_param, from_date_param, until_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        code = self.kwargs['code']
        interval = self.request.query_params.get('interval')
        model_cls = SensorsDataRollupAbstract.get_class_for_interval(interval)
        mid = Municipality.objects.filter(code=code).first().id
        eids = [e.id for e in Facility.objects.filter(municipality__id=mid)]
        ids = list([d.device_id for d in Device.objects.filter(educational_facility__id__in=eids)])
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        return model_cls.objects.filter(device_id__in=ids, time__date__gt=from_date, time__date__lt=until_date)

    serializer_class = SensorsDataRollupWithDeviceSerializer
    permission_classes = [AllowAny, ]


class SensorDataLastValuesList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve last readings for all devices",
                         operation_summary="Gets last Sensor data",
                         tags=['report'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = SensorDataLastValues.objects.all()
    serializer_class = SensorDataLastValuesSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class MyTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(operation_description="Gets API access token for given credentials",
                         operation_summary="Gets API access token",
                         tags=['token'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenViewBase):
    @swagger_auto_schema(operation_description="Refreshes API access token",
                         operation_summary="Gets refreshed API access token",
                         tags=['token'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    serializer_class = TokenRefreshSerializer
