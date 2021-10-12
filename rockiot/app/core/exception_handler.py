import traceback

from django.db import connection, transaction
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from app.core.api_response import ApiResponse

import logging

logger = logging.getLogger(__name__)


def handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """

    if isinstance(exc, Http404):
        return ApiResponse.not_found()

    elif isinstance(exc, PermissionDenied):
        set_rollback()
        return ApiResponse.access_denied(message=exc.detail, code=exc.status_code)

    if isinstance(exc, AuthenticationFailed):
        set_rollback()
        return ApiResponse.access_denied(message=exc.detail, code=exc.status_code)

    if isinstance(exc, exceptions.APIException):
        set_rollback()
        logger.error("api exception occurred: %s" % exc)
        return ApiResponse.error(message=exc.detail, code=exc.status_code)

    if isinstance(exc, ValueError) or isinstance(exc, KeyError):
        logger.error("key/value error occurred [error: %s]" % exc)
        logger.error(traceback.format_exc())
        return ApiResponse.bad_request()

    if isinstance(exc, BaseException):
        set_rollback()
        logger.error("base exception occurred: %s" % exc)
        logger.error(traceback.format_exc())
        return ApiResponse.error()

    return None


def set_rollback():
    atomic_requests = connection.settings_dict.get('ATOMIC_REQUESTS', False)
    if atomic_requests and connection.in_atomic_block:
        transaction.set_rollback(True)