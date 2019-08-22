# -*- coding: utf-8 -*-
# Filename: auth
# Author: brayton
# Datetime: 2019-Jul-18 10:39 AM

import jwt

from settings import JWT
from handler import exceptions
from models.user import User


class AnonymousUser:
    id = None
    username = ''
    is_active = False
    is_superuser = False
    _groups = []
    _user_permissions = []

    def __str__(self):
        return 'AnonymousUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return 1  # instances always return the same hash value

    def __int__(self):
        raise TypeError('Cannot cast AnonymousUser to int. Are you trying to use it in place of User?')


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.headers.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Header encoding (see RFC5987)
        auth = auth.encode('iso-8859-1')
    return auth


def jwt_decode_handler(token):
    options = {
        'verify_exp': JWT.VERIFY_EXPIRATION,
    }
    # get user from token, BEFORE verification, to get user secret key
    secret_key = JWT.SECRET_KEY
    return jwt.decode(
        token,
        JWT.PUBLIC_KEY or secret_key,
        JWT.VERIFY,
        options=options,
        leeway=JWT.LEEWAY,
        audience=JWT.AUDIENCE,
        issuer=JWT.ISSUER,
        algorithms=[JWT.ALGORITHM]
    )


class BaseAuthentication(object):
    """
    All authentication classes should extend BaseAuthentication.
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        raise NotImplementedError(".authenticate() must be overridden.")

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        pass


class JSONWebTokenAuthentication(BaseAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = JWT.AUTH_HEADER_PREFIX.lower()

        if not auth:
            if JWT.AUTH_COOKIE:
                return request.COOKIES.get(JWT.AUTH_COOKIE)
            return None

        if str(auth[0].lower(), encoding='utf-8') != auth_header_prefix:
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('无效的授权请求头，没有提身份凭证。')
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed('无效的授权头，凭据字符串不应包含空格。')

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(JWT.AUTH_HEADER_PREFIX, self.www_authenticate_realm)

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed('签名已过期！')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('解码签名时出错！')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        return user, jwt_value

    @staticmethod
    def authenticate_credentials(payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        auth_uid = payload.get('uuid')

        if not auth_uid:
            raise exceptions.AuthenticationFailed('无效的认证信息！')

        user = User.get_by_natural_key(auth_uid)
        print(user)
        if not user:
            raise exceptions.AuthenticationFailed('无效签名！')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('该用户已被禁用！')

        return user
