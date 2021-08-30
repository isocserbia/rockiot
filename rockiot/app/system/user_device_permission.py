import logging
from rest_framework import permissions
from app.models import Device, FacilityMembership

logger = logging.getLogger(__name__)


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
