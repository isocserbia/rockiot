from django.urls import path

from app.views import FacilityMapView, FacilityList, MyTokenObtainPairView, FacilityView, \
    SensorDataList, SensorDataLastValuesList, DevicesList, \
    MunicipalitySensorsSummary, FacilitySensorsSummary, DeviceSensorsSummary, MunicipalityList, MunicipalityView, \
    MyTokenRefreshView, CsvExportView

app_name = "app"

urlpatterns = [
    path("map/", FacilityMapView.as_view()),
    path('municipalities/', MunicipalityList.as_view(), name='facility-list'),
    path('municipalities/<code>/', MunicipalityView.as_view(), name='facility-list'),
    path('municipalities/<code>/data/aggregate/', MunicipalitySensorsSummary.as_view(), name='municipality-sensors-list'),
    path('facilities/', FacilityList.as_view(), name='facility-list'),
    path('facilities/<code>/', FacilityView.as_view(), name='facility-view'),
    path('facilities/<code>/data/aggregate/', FacilitySensorsSummary.as_view(), name='facility-sensors-list'),
    path('devices/', DevicesList.as_view(), name='device-list'),
    path('devices/data/raw/', CsvExportView.as_view(), name='device-sensors-last-values'),
    path('devices/data/last/', SensorDataLastValuesList.as_view(), name='device-sensors-last-values'),
    path('devices/<device_id>/data/aggregate/', DeviceSensorsSummary.as_view(), name='device-sensors-summary'),
    path('devices/<device_id>/data/row/', SensorDataList.as_view(), name='device-sensors-data'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
]