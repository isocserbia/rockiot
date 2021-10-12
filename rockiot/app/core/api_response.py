from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class ApiResponse:

    @staticmethod
    def ok(message="success", data=None, code=200):
        response = {"status": "OK", "message": (message if settings.DEBUG else "success"), "data": data}
        return ApiResponse.make(Response(response, status=code))

    @staticmethod
    def bad_request(error_code="error", message="bad request", data=None, code=400):
        response = {"status": "ERROR", "error": error_code, "message": (message if settings.DEBUG else "bad request"), "data": data}
        return ApiResponse.make(Response(response, status=code))

    @staticmethod
    def not_found(message="not found", code=404):
        response = {"status": "ERROR", "message": (message if settings.DEBUG else "not found")}
        return ApiResponse.make(Response(response, status=code))

    @staticmethod
    def access_denied(message="access_denied", code=403):
        response = {"status": "ERROR", "message": (message if settings.DEBUG else "access denied")}
        return ApiResponse.make(Response(response, status=code))

    @staticmethod
    def error(message="server error", code=500):
        response = {"status": "ERROR", "message": (message if settings.DEBUG else "server error")}
        return ApiResponse.make(Response(response, status=code))

    @staticmethod
    def make(response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        return response
