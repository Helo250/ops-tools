# -*- coding: utf-8 -*-
# Filename: alteration
# Author: brayton
# Datetime: 2019-Aug-13 12:08 PM


from motorengine import (
    StringField, IntField, BooleanField,
    DateTimeField, ReferenceField, UUIDField, ObjectIdField, ListField, EmbeddedDocumentField)

from .base import BaseDocument, JsonField


class Alteration(BaseDocument):
    title = StringField(max_length=64)
    product = StringField(max_length=32)
    execute_at = DateTimeField()
    reason = StringField(max_length=128)
    effect = StringField(max_length=128)
    sent_at = DateTimeField()
    sent_by = ListField(StringField())
    sent_to = ListField(JsonField())
