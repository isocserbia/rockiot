from django.urls import path

from app.views import EducationFacilityMapView, FacilityList, MyTokenObtainPairView, FacilityView, \
    SensorDataList, SensorDataLastValuesList, DevicesList, \
    MunicipalitySensorsSummary, FacilitySensorsSummary, DeviceSensorsSummary, MunicipalityList, MunicipalityView, \
    MyTokenRefreshView

app_name = "app"

urlpatterns = [
    path("map/", EducationFacilityMapView.as_view()),
    path('municipalities/', MunicipalityList.as_view(), name='facility-list'),
    path('municipalities/<code>/', MunicipalityView.as_view(), name='facility-list'),
    path('municipalities/<code>/sensors/summary/', MunicipalitySensorsSummary.as_view(), name='municipality-sensors-list'),
    path('facilities/', FacilityList.as_view(), name='facility-list'),
    path('facilities/<code>/', FacilityView.as_view(), name='facility-view'),
    path('facilities/<code>/sensors/summary/', FacilitySensorsSummary.as_view(), name='facility-sensors-list'),
    path('devices/', DevicesList.as_view(), name='device-list'),
    path('devices/<device_id>/sensors/summary/', DeviceSensorsSummary.as_view(), name='device-sensors-summary'),
    path('devices/<device_id>/sensors/data/', SensorDataList.as_view(), name='device-sensors-data'),
    path('devices/sensors/values/last/', SensorDataLastValuesList.as_view(), name='device-sensors-last-values'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
]