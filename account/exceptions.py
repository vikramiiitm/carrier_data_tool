from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.exceptions import DetailDictMixin
from django.utils.translation import ugettext_lazy as _


class TokenError(Exception):
    pass

class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Incorrect authentication credentials.')
    default_code = 'authentication_failed'

class AuthenticationFailed(DetailDictMixin, AuthenticationFailed):
    pass

class InvalidToken(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Token is invalid or expired")
    default_code = "token_not_valid"