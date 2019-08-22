# -*- coding: utf-8 -*-
# Filename: account
# Author: brayton
# Datetime: 2019-Aug-15 10:11 AM


from motorengine import (
    StringField, IntField, BooleanField,
    DateTimeField, UUIDField, ObjectIdField, ListField, URLField)

from .base import BaseDocument, JsonField, ReferenceField


third_party_platform = [

]


class ThirdPartyPlatform(BaseDocument):
    """
    authentication:
        [{
            'type': 'text',
            'label': '账户',
            'name': 'account',
            'required': true
        },
        {
            'type': text,
            'label':'密码',
            'name': 'password'，
            'required': true
        }]
    """
    name = StringField(max_length=32)
    code = StringField(max_length=32)
    authentication = ListField(JsonField())


class Account(BaseDocument):
    name = StringField(max_length=64)
    platform = StringField(max_length=32)
    account = StringField(max_length=32)
    password = StringField(max_length=128)
    access = JsonField()
    url = StringField(max_length=65535)
    parent = ReferenceField(reference_document_type='models.account.Account')
    adaptor = StringField(max_length=32)

    @property
    def children(self):
        return self.objects.find_all(parent=self._id)






