import logging
from rest_framework import permissions
from app.models import FacilityMembership, Facility, Device

logger = logging.getLogger(__name__)


class UserFacilityPermission(permissions.BasePermission):
    """
    Permission to allow user for requested facility
    """

    def has_permission(self, request, view):

        if not request.user:
            logger.warning("no user in request [path: %s]" % request.get_full_path)
            return False

        code = request.resolver_match.kwargs.get('code') if request.resolver_match.kwargs.get('code') \
            else view.kwargs.get('code')

        if not code:
            logger.warning("no code parameter in request data [user: %s] [path: %s]" %
                           (request.user, request.get_full_path))
            return False

        facility = Facility.objects.filter(code=code).first()
        if not facility:
            logger.warning("no such facility [user: %s] [facility: %s] [path: %s]" %
                           (request.user, code, request.get_full_path))
            return False

        member = FacilityMembership.objects.filter(facility=facility,
                                                   user=request.user).first()
        if not member:
            logger.warning("no membership for facility [user: %s] [facility: %s] [path: %s]" %
                           (request.user, code, request.get_full_path))
            return False

        logger.debug("permission granted [user: %s] [code: %s] [path: %s]" %
                     (request.user, code, request.get_full_path))
        return True


class UserDevicePermission(permissions.BasePermission):
    """
    Permission to allow user for requested device
    """

    def has_permission(self, request, view):

        if not request.user:
            logger.warning("no user in request [path: %s]" % request.get_full_path)
            return False

        device_id = request.resolver_match.kwargs.get('device_id') if request.resolver_match.kwargs.get('device_id') \
            else view.kwargs.get('device_id')

        if not device_id:
            logger.warning("no device_id parameter in request data [user: %s] [path: %s]" %
                           (request.user.email, request.get_full_path))
            return False

        device = Device.objects.filter(device_id=device_id).first()
        if not device:
            logger.warning("no such device [user: %s] [device_id: %s] [path: %s]" %
                           (request.user.email, device_id, request.get_full_path))
            return False

        member = FacilityMembership.objects.filter(facility=device.facility,
                                                   user=request.user).first()
        if not member:
            logger.warning("no membership for device [user: %s] [device_id: %s] [path: %s]" %
                           (request.user.email, device_id, request.get_full_path))
            return False

        logger.debug("permission granted [user: %s] [device_id: %s] [path: %s]" %
                     (request.user.email, device_id, request.get_full_path))
        return True
