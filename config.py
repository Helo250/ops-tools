# coding:utf-8

import os
import datetime


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'this is a secret key'

APPLICATION = {
    'debug': True,
    'default_handler_class': 'handler.web.APIDefaultHandler',
    'allow_remote_access': True,
    'template_path': os.path.join(os.path.dirname(__file__), "template"),
    'static_path': os.path.join(os.path.dirname(__file__), "static"),
    'cookie_secret': 'this is a secret'
}

# MongoDB Config
MONGODB = {
    'host': 'localhost',
    'port': 27017,
    'name': 'test',
    'username': None,
    'password': None
}

JWT_AUTH = {
    'SECRET_KEY': SECRET_KEY,
    'GET_USER_SECRET_KEY': None,
    'PUBLIC_KEY': None,
    'PRIVATE_KEY': None,
    'ALGORITHM': 'HS256',
    'VERIFY': True,
    'VERIFY_EXPIRATION': True,
    'LEEWAY': 0,
    'EXPIRATION_DELTA': datetime.timedelta(seconds=30000),
    'AUDIENCE': None,
    'ISSUER': None,

    'ALLOW_REFRESH': True,
    'REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'AUTH_HEADER_PREFIX': 'JWT',
    'AUTH_COOKIE': None,
}

# You can generate the key by the following website:
# https://asecuritysite.com/encryption/keygen
AES_KEY = 'your 32 byte aes key'
TOKEN_TIMEOUT = 60 * 60 * 24 * 30

