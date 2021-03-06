"""Markers view."""
import logging
from datetime import date, datetime, timedelta

from django.conf import settings
from django.db.models import Prefetch
from django.http import FileResponse, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, views
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase

from app import models
from app.models import Facility, SensorData, SensorDataLastValues, Device, Municipality, \
    SensorsDataRollupAbstract, SensorDataRaw
from app.serializers import FacilityModelSerializer, MyTokenObtainPairSerializer, \
    SensorDataLastValuesSerializer, DeviceModelSerializer, \
    SensorsDataRollupWithDeviceSerializer, SensorDataSerializer, DeviceLogEntrySerializer, \
    SensorAverageMunicipalitySerializer, \
    SensorAverageFacilitySerializer, SensorDataRawAllSerializer, DeviceReadingsSerializer, SensorsDataRollupSerializer, \
    MunicipalityWithFacilitiesModelSerializer
from app.tasks import export_raw_data_to_csv

logger = logging.getLogger(__name__)

config = settings.REST_FRAMEWORK


class IndexView(TemplateView):
    template_name = "index.html"


from_date_param = openapi.Parameter('from_date', openapi.IN_QUERY,
                                    description="Starting from date",
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME)

until_date_param = openapi.Parameter('until_date', openapi.IN_QUERY,
                                     description="Until date",
                                     type=openapi.TYPE_STRING,
                                     format=openapi.FORMAT_DATETIME)


class DevicesList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of Device entities",
                         operation_summary="Gets all Devices",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Device.objects.defer("metadata").all()
    serializer_class = DeviceModelSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = int(config['PAGE_SIZE'])


class DeviceChangeLogList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve Device changelog",
                         operation_summary="Get device changelog",
                         tags=['report'],
                         manual_parameters=[from_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        did = self.kwargs['device_id']
        device = get_object_or_404(Device, device_id=did)
        from_date = self.request.query_params.get('from_date', None)
        if from_date is not None:
            from_date_date = datetime.fromisoformat(from_date)
            return device.history.filter(history_date__date__gte=from_date_date)
        else:
            return device.history.all()

    serializer_class = DeviceLogEntrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


class MunicipalityView(generics.RetrieveAPIView):
    @swagger_auto_schema(operation_description="Retrieve single Municipality entity",
                         operation_summary="Gets Municipality by code",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        code = self.kwargs['code']
        return get_object_or_404(Municipality.objects, code=code)

    serializer_class = MunicipalityWithFacilitiesModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]


class MunicipalityList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of all Municipality entities",
                         operation_summary="Gets all Municipalities",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Municipality.objects.all()
    serializer_class = MunicipalityWithFacilitiesModelSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])


class FacilityView(generics.RetrieveAPIView):
    @swagger_auto_schema(operation_description="Retrieve single Facility entity",
                         operation_summary="Gets Facility by code",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        code = self.kwargs['code']
        return get_object_or_404(Facility.objects, code=code)

    serializer_class = FacilityModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]


class FacilityList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of all Facility entities",
                         operation_summary="Gets all Facilities",
                         tags=['core'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = Facility.objects.all()
    serializer_class = FacilityModelSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])


class SensorDataList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve calibrated and cleaned sensor data reading",
                         operation_summary="Gets calibrated and cleaned Sensor data for single Device",
                         tags=['report'],
                         manual_parameters=[from_date_param, until_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        did = self.kwargs['device_id']
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        qs1 = SensorData.objects.filter(device_id=did)
        if from_date is not None:
            qs1 = qs1.filter(time__date__gte=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lte=until_date)
        return qs1

    serializer_class = SensorDataSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


class SensorDataRawList(generics.ListAPIView):
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
            qs1 = qs1.filter(time__date__gte=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lte=until_date)
        return qs1

    serializer_class = SensorDataRawAllSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


interval_param = openapi.Parameter('interval', openapi.IN_QUERY,
                                   description="interval ('15m','1h','4h','24h')",
                                   type=openapi.TYPE_STRING, default='1h')

facility_code = openapi.Parameter('facility', openapi.IN_QUERY,
                                  description="Facility code",
                                  type=openapi.TYPE_STRING)

municipality_code = openapi.Parameter('municipality', openapi.IN_QUERY,
                                      description="Municipality code",
                                      type=openapi.TYPE_STRING)

mode_param = openapi.Parameter('mode', openapi.IN_QUERY,
                               description="Device mode",
                               type=openapi.TYPE_STRING, default=Device.PRODUCTION)


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
            qs1 = qs1.filter(time__date__gte=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lte=until_date)
        return qs1

    serializer_class = SensorsDataRollupSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


class AllDeviceSensorsSummary(generics.ListAPIView):
    @swagger_auto_schema(
        operation_description="Retrieve list of aggregated Sensor data for all devices in last 24h",
        operation_summary="Gets aggregated Sensor data for all device in last 24h",
        tags=['report'],
        manual_parameters=[interval_param, facility_code, municipality_code, mode_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        interval = self.request.query_params.get('interval')
        facility_code_val = self.request.query_params.get('facility')
        municipality_code_val = self.request.query_params.get('municipality')
        mode_param_val = self.request.query_params.get('mode', '').upper()
        mode_param_val = mode_param_val if Device.is_known_mode(mode_param_val) else None
        model_cls = SensorsDataRollupAbstract.get_class_for_interval(interval)
        sdq = model_cls.objects.filter(time__gt=datetime.now() - timedelta(days=1))
        devq = Device.objects.all() if mode_param_val is None else Device.objects.filter(mode=mode_param_val)
        if facility_code_val is not None:
            devq = devq.filter(facility__code=facility_code_val)
        elif municipality_code_val is not None:
            devq = devq.filter(facility__municipality__code=municipality_code_val)
        devq = devq.only("device_id", "facility").prefetch_related(
                Prefetch('facility', queryset=Facility.objects.all().only('id', 'code', 'municipality__code')))
        result = devq.prefetch_related(Prefetch(model_cls.get_related_name(), queryset=sdq))
        return result

    def get_serializer_class(self):
        return DeviceReadingsSerializer.get_serializer_class(self.request.query_params.get("interval"))

    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) / 2)


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
        ids = list([d.device_id for d in Device.objects.only("device_id").filter(facility__code=code)])
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        qs1 = model_cls.objects.filter(device_id__in=ids)
        if from_date is not None:
            qs1 = qs1.filter(time__date__gte=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lte=until_date)
        return qs1

    serializer_class = SensorsDataRollupWithDeviceSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


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
        eids = [e.id for e in Facility.objects.only("id", "municipality").filter(municipality__id=mid)]
        ids = list([d.device_id for d in Device.objects.only("device_id", "facility").filter(facility__id__in=eids)])
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        qs1 = model_cls.objects.filter(device_id__in=ids)
        if from_date is not None:
            qs1 = qs1.filter(time__date__gte=from_date)
        if until_date is not None:
            qs1 = qs1.filter(time__date__lte=until_date)
        return qs1

    serializer_class = SensorsDataRollupWithDeviceSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


class SensorDataAverageMunicipality(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of average Sensor data for Municipality",
                         operation_summary="Gets average Sensor data for Municipality",
                         tags=['report'],
                         manual_parameters=[interval_param, from_date_param, until_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        code = self.kwargs['code']
        interval = self.request.query_params.get('interval')
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        qs = getattr(models, f"Sensor{interval or '1h'}AverageMunicipality").objects.filter(code=code)
        if from_date is not None:
            qs = qs.filter(time__date__gte=from_date)
        if until_date is not None:
            qs = qs.filter(time__date__lte=until_date)
        return qs.order_by('-time')

    serializer_class = SensorAverageMunicipalitySerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


class SensorDataAverageFacility(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve list of average Sensor data for Facility",
                         operation_summary="Gets average Sensor data for Facility",
                         tags=['report'],
                         manual_parameters=[interval_param, from_date_param, until_date_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        code = self.kwargs['code']
        interval = self.request.query_params.get('interval')
        from_date = self.request.query_params.get('from_date', None)
        until_date = self.request.query_params.get('until_date', None)
        qs = getattr(models, f"Sensor{interval or '1h'}AverageFacility").objects.filter(code=code)
        if from_date is not None:
            qs = qs.filter(time__date__gte=from_date)
        if until_date is not None:
            qs = qs.filter(time__date__lte=until_date)
        return qs.order_by('-time')

    serializer_class = SensorAverageFacilitySerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])
    pagination_class.max_limit = (int(config['PAGE_SIZE']) * 10)


class SensorDataLastValuesList(generics.ListAPIView):
    @swagger_auto_schema(operation_description="Retrieve last readings for all devices",
                         operation_summary="Gets last Sensor data",
                         tags=['report'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    queryset = SensorDataLastValues.objects.all()
    serializer_class = SensorDataLastValuesSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = int(config['PAGE_SIZE'])


class CsvExportView(views.APIView):
    @swagger_auto_schema(operation_description="Get CSV file with raw sensor data for given date",
                         operation_summary="Download daily raw sensor data as CSV",
                         manual_parameters=[from_date_param],
                         tags=['report'],
                         responses={
                             '200': openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE)),
                             '201': 'System is creating file. Check later.',
                             '404': 'Not Found'
                         },
                         produces='text/csv')
    def get(self, request, format=None):
        from_date = self.request.query_params.get('from_date', date.today().isoformat())
        file_name = f'sensor_data-{from_date}.csv'
        file_path = f'/rockiot-data/{file_name}'
        try:
            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            return response
        except IOError as ioe:
            export_raw_data_to_csv.apply_async((from_date,))
            logger.info(f"System is creating CSV report [dat: {from_date}]")
            return HttpResponse('System is creating CSV report. Please, check again soon.')
        except:
            msg = f"Failed getting CSV file {file_name}"
            logger.error(msg, exc_info=True)
            raise HttpResponseServerError(msg)


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
