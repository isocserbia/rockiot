from django.urls import path
from django.views.decorators.cache import cache_page

from app.views import FacilityList, MyTokenObtainPairView, FacilityView, \
    SensorDataRawList, SensorDataLastValuesList, DevicesList, \
    MunicipalitySensorsSummary, FacilitySensorsSummary, DeviceSensorsSummary, MunicipalityList, MunicipalityView, \
    MyTokenRefreshView, CsvExportView, SensorDataList, DeviceChangeLogList, IndexView, SensorDataAverageMunicipality, \
    SensorDataAverageFacility

app_name = "app"

urlpatterns = [
    path("", IndexView.as_view()),
    path('municipalities/', cache_page(60 * 2)(MunicipalityList.as_view()), name='municipality-list'),
    path('municipalities/<code>/', cache_page(60)(MunicipalityView.as_view()), name='municipality-view'),
    # path('municipalities/<code>/data/aggregate/', MunicipalitySensorsSummary.as_view(), name='municipality-data-aggregate'),
    path('municipalities/<code>/data/aggregate/', cache_page(60)(SensorDataAverageMunicipality.as_view()), name='municipality-data-average'),
    path('facilities/', cache_page(60 * 2)(FacilityList.as_view()), name='facility-list'),
    path('facilities/<code>/', cache_page(60)(FacilityView.as_view()), name='facility-view'),
    # path('facilities/<code>/data/aggregate/', FacilitySensorsSummary.as_view(), name='facility-data-aggregate'),
    path('facilities/<code>/data/aggregate/', cache_page(60)(SensorDataAverageFacility.as_view()), name='facility-data-average'),
    path('devices/', cache_page(60 * 2)(DevicesList.as_view()), name='device-list'),
    path('devices/data/last/', cache_page(60)(SensorDataLastValuesList.as_view()), name='device-last-values'),
    path('devices/data/daily/csv/', CsvExportView.as_view(), name='devices-raw-daily-csv'),
    path('devices/<device_id>/data/aggregate/', cache_page(60)(DeviceSensorsSummary.as_view()), name='device-data-aggregate'),
    path('devices/<device_id>/data/raw/', cache_page(60)(SensorDataRawList.as_view()), name='device-data-raw'),
    path('devices/<device_id>/data/', cache_page(60)(SensorDataList.as_view()), name='device-data-clean'),
    path('devices/<device_id>/changelog/', cache_page(60*5)(DeviceChangeLogList.as_view()), name='device-changelog'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
]