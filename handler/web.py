# coding:utf-8

from utils.json import dumps
import traceback
from tornado.web import RequestHandler, HTTPError
from handler import status, exceptions
from utils.token import token_manager
from utils.auth import JSONWebTokenAuthentication

AnonymousUser = {
    'id': None,
    'username': None,
    'is_active': False
}


class APIRequestHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, application, request, **kwargs):
        RequestHandler.__init__(self, application, request, **kwargs)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

        if self.settings['allow_remote_access']:
            self.access_control_allow()

    def access_control_allow(self):
        # 允许 JS 跨域调用
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        # self.set_header("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, "
        #                                                 "X-Requested-With, X-Requested-By, If-Modified-Since, "
        #                                                 "X-File-Name, Cache-Control, Token")
        self.set_header("Access-Control-Allow-Headers", '*')
        self.set_header('Access-Control-Allow-Origin', '*')

    def _not_authenticated(self):
        self.current_user = AnonymousUser
        self.auth = None

    def _authenticate(self):
        for authenticator in (JSONWebTokenAuthentication, ):
            try:
                user_auth_tuple = authenticator().authenticate(self.request)
            except exceptions.APIException:
                self._not_authenticated()
                raise

            if user_auth_tuple is not None:
                self._authenticator = authenticator
                self.current_user, self.auth = user_auth_tuple
                return

        self._not_authenticated()

    def check_request_authentication(self):
        try:
            self._authenticate()
        except exceptions.APIException as e:
            self._handle_request_exception(e)

    def check_request_permissions(self):
        pass

    def prepare(self):
        super(APIRequestHandler, self).prepare()
        self.check_request_authentication()
        self.check_request_permissions()

    async def get(self, *args, **kwargs):
        raise exceptions.MethodNotAllowed()

    async def post(self, *args, **kwargs):
        raise exceptions.MethodNotAllowed()

    async def put(self, *args, **kwargs):
        raise exceptions.MethodNotAllowed()

    async def delete(self, *args, **kwargs):
        raise exceptions.MethodNotAllowed()

    async def options(self, *args, **kwargs):
        if self.settings['allow_remote_access']:
            self.write("")

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = dict()
            for arg, v in self.request.body_arguments.items():
                self._data[arg] = v
        return self._data

    def write_error(self, status_code, **kwargs):
        # TODO: remove it
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)

            self.write_json(dict(traceback=''.join(lines)), status_code, self._reason)

        else:
            self.write_json(None, status_code, self._reason)

    def write_json(self, data, status_code=200, msg='success.'):
        self.finish(dumps({
            'code': status_code,
            'msg': msg,
            'data': data
            }, indent=2, sort_keys=True, ensure_ascii=False)
        )



    def is_logined(self):
        if 'Token' in self.request.headers:
            token = self.request.headers['Token']
            logined, uid = token_manager.validate_token(token)

            if logined:
                # 已经登陆
                return uid

        # 尚未登陆
        raise HTTPError(status_code=status.HTTP_401_UNAUTHORIZED)

    # @staticmethod
    # def validate_id(_id):
    #     if _id is None or not ObjectId.is_valid(_id):
    #         raise HTTPError(**status.status_3)
    #
    # @staticmethod
    # def check_none(resource):
    #     if resource is None:
    #         raise HTTPError(**status.status_22)


class APIDefaultHandler(APIRequestHandler):
    def data_received(self, chunk):
        pass

    async def get(self, *args, **kwargs):
        raise exceptions.NotFound()

    async def post(self, *args, **kwargs):
        raise exceptions.NotFound()

    async def put(self, *args, **kwargs):
        raise exceptions.NotFound()

    async def delete(self, *args, **kwargs):
        raise exceptions.NotFound()

    async def options(self, *args, **kwargs):
        if self.settings['allow_remote_access']:
            self.write("")

    def check_xsrf_cookie(self):
        # POSTs to an ErrorHandler don't actually have side effects,
        # so we don't need to check the xsrf token.  This allows POSTs
        # to the wrong url to return a 404 instead of 403.
        pass
