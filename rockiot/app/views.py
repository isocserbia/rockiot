"""Markers view."""
import logging
from datetime import date

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, views
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase

from app.models import Facility, SensorData, SensorDataLastValues, Device, Municipality, \
    SensorsDataRollupAbstract, SensorDataRaw
from app.serializers import FacilityModelSerializer, MyTokenObtainPairSerializer, SensorDataSerializer, \
    SensorDataLastValuesSerializer, DeviceModelSerializer, \
    SensorsDataRollupSerializer, MunicipalityModelSerializer, SensorsDataRollupWithDeviceSerializer

logger = logging.getLogger(__name__)


class FacilityMapView(TemplateView):
    template_name = "map.html"


class DevicesList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of Device entities",
                         operation_summary="Gets all Devices",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Device.objects.all()
    serializer_class = DeviceModelSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


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
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


class MunicipalityList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of all Municipality entities",
                         operation_summary="Gets all Municipalities",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Municipality.objects.all()
    serializer_class = MunicipalityModelSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


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
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


class FacilityList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of all Facility entities",
                         operation_summary="Gets all Facilities",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Facility.objects.all()
    serializer_class = FacilityModelSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


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
        qs1 = SensorDataRaw.objects.filter(device_id=did)
        if from_date is not None:
            qs1 = qs1.filter(time__date__gt=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lt=until_date)
        return qs1

    serializer_class = SensorDataSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]  # UserDevicePermission


interval_param = openapi.Parameter('interval', openapi.IN_QUERY,
                                   description="interval ('15m','1h','4h','24h')",
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
        qs1 = model_cls.objects.filter(device_id=device_id)
        if from_date is not None:
            qs1 = qs1.filter(time__date__gt=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lt=until_date)
        return qs1

    serializer_class = SensorsDataRollupSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


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
        ids = list([d.device_id for d in Device.objects.filter(facility__code=code)])
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        qs1 = model_cls.objects.filter(device_id__in=ids)
        if from_date is not None:
            qs1 = qs1.filter(time__date__gt=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lt=until_date)
        return qs1

    serializer_class = SensorsDataRollupWithDeviceSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


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
        ids = list([d.device_id for d in Device.objects.filter(facility__id__in=eids)])
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        qs1 = model_cls.objects.filter(device_id__in=ids)
        if from_date is not None:
            qs1 = qs1.filter(time__date__gt=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lt=until_date)
        return qs1

    serializer_class = SensorsDataRollupWithDeviceSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


class SensorDataLastValuesList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve last readings for all devices",
                         operation_summary="Gets last Sensor data",
                         tags=['report'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = SensorDataLastValues.objects.all()
    serializer_class = SensorDataLastValuesSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


class CsvExportView(views.APIView):
    @swagger_auto_schema(operation_description="Get CSV file with raw sensor data for given date",
                         operation_summary="Download daily raw sensor data as CSV",
                         manual_parameters=[from_date_param],
                         tags=['report'],
                         responses={
                             '200': openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE)),
                             '404': 'Not Found'
                         },
                         produces='text/csv')
    def get(self, request, format=None):
        from_date = self.request.query_params.get('from_date', date.today().isoformat())
        file_name = f'sensor_data-{from_date}.csv'
        try:
            file_handle = open(f'/rockiot-data/{file_name}', 'rb')
            response = FileResponse(file_handle, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            return response
        except IOError as ioe:
            meg = f"Requested CSV file {file_name} not found: {ioe}"
            logger.warning(meg)
            raise Http404(meg)


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
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]


class MyTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(operation_description="Fetches new API access token for given credentials",
                         operation_summary="Fetch API access token",
                         tags=['token'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenViewBase):
    @swagger_auto_schema(operation_description="Refreshes API access token",
                         operation_summary="Fetch refreshed API access token",
                         tags=['token'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    serializer_class = TokenRefreshSerializer
