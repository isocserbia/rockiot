"""rockiot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from app.models import Device, Municipality

from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="ROCKIOT API",
        default_version='v1',
        description="ROCKIOT description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@rockiot.org"),
        license=openapi.License(name="APACHE2 License"),
    ),
    url=settings.SERVING_URL,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def read_file(request):
    with open('../app/migrations/geojson/serbia.json', 'r') as file:
        return HttpResponse(file, content_type="text/plain")


urlpatterns = [
   url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   path('admin/', admin.site.urls),
   path("api/", include("app.urls")),
   url(r'^ht/', include('health_check.urls')),
   url('', include('django_prometheus.urls')),
   url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
   url(r'^data.geojson$',
       GeoJSONLayerView.as_view(model=Device, geometry_field="location", properties=('device_id', 'mode', 'status')),
       name='data'),
   url(r'^borders.geojson$',
       GeoJSONLayerView.as_view(model=Municipality, geometry_field="area", properties=('id', 'code', 'name', 'area')),
       name='borders'),
]
