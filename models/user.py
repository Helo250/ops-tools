# -*- coding: utf-8 -*-
# Filename: user
# Author: brayton
# Datetime: 2019-Jul-17 5:38 PM

from motorengine import BaseField, StringField, ObjectIdField, BooleanField, EmailField

from .base import BaseDocument
from .utils import MobileField


class User(BaseDocument):
    email = EmailField(required=False)
    mobile = MobileField(required=False)
    nickname = StringField(required=True, max_length=32)
    auth_uid = StringField(required=True)
    is_active = BooleanField(default=True)

    @classmethod
    def get_by_natural_key(cls, auth_uid):
        return cls.object(auth_uid=auth_uid)




