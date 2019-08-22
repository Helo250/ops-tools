# -*- coding: utf-8 -*-
# Filename: exceptions
# Author: brayton
# Datetime: 2019-Jul-18 11:51 AM

from tornado.web import HTTPError

from handler import status


class APIException(HTTPError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_errcode = 'error'
    default_errmsg = '服务异常！'

    def __init__(self, log_message=None, *args, **kwargs):
        self.errcode = kwargs.get('errcode', self.default_errcode)
        self.errmsg = kwargs.get('errmsg', self.default_errmsg)
        if 'reason' not in kwargs:
            kwargs['reason'] = f'ErrorDetails: (code: {self.errcode}, string: {self.errmsg})'
        super(APIException, self).__init__(self.status_code, None, *args, **kwargs)


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_errcode = 'authentication_failed'
    default_errmsg = '用户认证失败！'


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_errmsg = '未提供身份验证凭据！'
    default_errcode = 'not_authenticated'


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_errmsg = '您没有执行此操作的权限！'
    default_errcode = 'permission_denied'


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_errmsg = '网页已经被吃掉了.'
    default_errcode = 'not_found'


class MethodNotAllowed(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_errmsg = '当前请求不被允许.'
    default_errcode = 'method_not_allowed'


class NotAcceptable(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_errmsg = '无法满足请求接受头.'
    default_errcode = 'not_acceptable'


class Throttled(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_errmsg = '过于频繁，请求已被阻止.'
    default_errcode = 'throttled'


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_errmsg = '请携带正确的内容'
    default_errcode = 'invalid'


class ParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_errmsg = '解析出错'
    default_errcode = 'parse_error'
