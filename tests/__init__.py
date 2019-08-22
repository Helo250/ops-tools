# -*- coding: utf-8 -*-
# Filename: __init__.py
# Author: brayton
# Datetime: 2019-Jul-23 3:55 PM

from tornado.options import define
import json
define("port", group='Webserver', type=int, default=8500, help="Run on the given port")
define("subpath", group='Webserver', type=str, default="/api", help="Url subpath (such as /nebula)")
define('unix_socket', group='Webserver', default=None, help='Path to unix socket to bind')

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from settings import MONGODB, SERVER
from pymongo.mongo_client import MongoClient
from motorengine.connection import register_connection, DEFAULT_CONNECTION_NAME
from pymongo.errors import ConnectionFailure
from handler.patch import patch_all
patch_all()


import os
os.environ.setdefault('ASYNC_TEST_TIMEOUT', '5')


class WebTestCase(AsyncHTTPTestCase):
    """Base class for web tests that also supports WSGI mode.

    Override get_handlers and get_app_kwargs instead of get_app.
    Append to wsgi_safe to have it run in wsgi_test as well.
    """

    def setUp(self):
        super(WebTestCase, self).setUp()
        self.setup_mongo(MONGODB.name, host=MONGODB.host, port=MONGODB.port)

    def setup_mongo(self, db_name, **config):
        def pre_connect():
            test_config = dict(
                **config,
                serverselectiontimeoutms=500
            )
            try:
                # The ismaster command is cheap and does not require auth.
                MongoClient(**test_config).admin.command('ismaster')
                return True
            except ConnectionFailure:
                return False

        if not pre_connect():
            raise Exception('The mongodb deamon is down or the configure is error!')
        else:
            register_connection(db_name, DEFAULT_CONNECTION_NAME, **config)


    def get_app(self):
        self.app = Application(handlers=self.get_handlers(), **self.get_app_kwargs())
        return self.app

    def get_handlers(self):
        raise NotImplementedError()

    def process_body(self, body):
        result = json.loads(body.decode())
        return result

    def prepare_body(self, body):
        return json.dumps(body).encode()

    def get_app_kwargs(self):
        return dict(
            template_path=SERVER.template_path,
            static_path=SERVER.static_path,
            debug=SERVER.debug,
            cookie_secret=SERVER.cookie_secret,
            allow_remote_access=SERVER.allow_remote_access,
            default_handler_class=SERVER.default_handler_class
        )

    def fetch(self, path, raise_error=False, **kwargs):
        kwargs.setdefault('headers', {
                'Content-Type': 'application/json;charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        return super(WebTestCase, self).fetch(path, raise_error, **kwargs)
