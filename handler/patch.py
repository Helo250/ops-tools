# -*- coding: utf-8 -*-
# Filename: patch
# Author: brayton
# Datetime: 2019-Jul-25 3:45 PM

import codecs
import json
from tornado.httputil import parse_body_arguments as _parse_body_arguments
from tornado import httputil

from .exceptions import ParseError


def parse_body_arguments(content_type, body, arguments, files, headers=None):
    _parse_body_arguments(content_type, body, arguments, files, headers)
    if content_type.startswith("application/json"):
        try:
            # decoded_body = codecs.getreader('utf-8')(body)
            decoded_body = body.decode('utf-8')
            if decoded_body:
                # for name, value in json.loads(decoded_body).items():
                #     arguments.setdefault(name, []).
                arguments.update(json.loads(decoded_body))
        except ValueError as e:
            raise ParseError(f'JSON parse error - {e}')


def patch_all():
    setattr(httputil, 'parse_body_arguments', parse_body_arguments)

