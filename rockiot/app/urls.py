from django.urls import path

from app.views import FacilityMapView, FacilityList, MyTokenObtainPairView, FacilityView, \
    SensorDataRawList, SensorDataLastValuesList, DevicesList, \
    MunicipalitySensorsSummary, FacilitySensorsSummary, DeviceSensorsSummary, MunicipalityList, MunicipalityView, \
    MyTokenRefreshView, CsvExportView, SensorDataList, DeviceChangeLogList

app_name = "app"

urlpatterns = [
    path("map/", FacilityMapView.as_view()),
    path('municipalities/', MunicipalityList.as_view(), name='facility-list'),
    path('municipalities/<code>/', MunicipalityView.as_view(), name='facility-list'),
    path('municipalities/<code>/data/aggregate/', MunicipalitySensorsSummary.as_view(), name='municipality-data-aggregate'),
    path('facilities/', FacilityList.as_view(), name='facility-list'),
    path('facilities/<code>/', FacilityView.as_view(), name='facility-view'),
    path('facilities/<code>/data/aggregate/', FacilitySensorsSummary.as_view(), name='facility-data-aggregate'),
    path('devices/', DevicesList.as_view(), name='device-list'),
    path('devices/data/last/', SensorDataLastValuesList.as_view(), name='device-last-values'),
    path('devices/data/daily/csv/', CsvExportView.as_view(), name='devices-raw-daily-csv'),
    path('devices/<device_id>/data/aggregate/', DeviceSensorsSummary.as_view(), name='device-data-aggregate'),
    path('devices/<device_id>/data/raw/', SensorDataRawList.as_view(), name='device-data-raw'),
    path('devices/<device_id>/data/', SensorDataList.as_view(), name='device-data-clean'),
    path('devices/<device_id>/changelog/', DeviceChangeLogList.as_view(), name='device-changelog'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
]