import logging
from rest_framework import permissions
from app.models import Device, EducationalFacilityMembership, EducationFacility

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

        educational_facility = EducationFacility.objects.filter(slug=code).first()
        if not educational_facility:
            logger.warning("no such facility [user: %s] [facility: %s] [path: %s]" %
                           (request.user, code, request.get_full_path))
            return False

        member = EducationalFacilityMembership.objects.filter(educational_facility=educational_facility,
                                                              user=request.user).first()
        if not member:
            logger.warning("no membership for facility [user: %s] [facility: %s] [path: %s]" %
                           (request.user, code, request.get_full_path))
            return False

        logger.debug("permission granted [user: %s] [code: %s] [path: %s]" %
                     (request.user, code, request.get_full_path))
        return True
