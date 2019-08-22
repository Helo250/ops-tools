# -*- coding: utf-8 -*-
# Filename: events
# Author: brayton
# Datetime: 2019-Jul-17 4:59 PM

from motorengine import (
    StringField, IntField, BooleanField,
    DateTimeField, ReferenceField, UUIDField, ObjectIdField, ListField, EmbeddedDocumentField)

from .base import BaseDocument, JsonField


class School(BaseDocument):
    name = StringField(required=True)
    verifier = StringField()


class EventStatus(BaseDocument):
    class Meta:
        fields_map = dict()
        verbose_name = 'eventStatus'
    code = StringField(required=True, max_length=16)
    name = StringField(required=True, max_length=64)


class EventLevel(BaseDocument):
    # class Meta:
    #     fields_map = dict()
    #     verbose_name = 'eventLevel'
    code = StringField(required=True, max_length=16)
    name = StringField(required=True, max_length=32)


class Event(BaseDocument):
    name = StringField(required=True, max_length=255)
    status = StringField(required=True, max_length=16)
    level = StringField(required=True, max_length=16)
    started_at = DateTimeField(required=True)
    ended_at = DateTimeField(required=True)
    # created_by = ReferenceField(reference_document_type=User)
    created_at = DateTimeField(required=True, auto_now_on_insert=True)
    participants = ListField(JsonField(required=True))
