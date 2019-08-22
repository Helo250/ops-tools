# -*- coding: utf-8 -*-
# Filename: message
# Author: brayton
# Datetime: 2019-Jul-29 10:38 AM

from motorengine import (
    StringField, IntField, BooleanField,
    DateTimeField, ReferenceField, UUIDField, ObjectIdField, ListField , EmbeddedDocumentField)

from .base import BaseDocument, JsonField
from data.example import MessageStatusEnum, DefaultMessageSchedule
from utils import get_next_day


class NotifyMedia(BaseDocument):
    name = StringField()
    code = StringField()
    disabled = BooleanField(default=False)


class NotifySchedule(BaseDocument):
    code = StringField()
    name = StringField()


class Message(BaseDocument):
    # 消息内容
    title = StringField(max_length=64)
    content = StringField(max_length=500)
    comment = StringField(max_length=200)
    # 发送信息
    sent_from = JsonField()
    sent_at = DateTimeField()
    sent_by = ListField(StringField())
    sent_to = ListField(JsonField())
    next_sent_at = DateTimeField()
    # 管理信息
    created_at = DateTimeField(auto_now_on_insert=True)
    # created_by = ReferenceField()
    updated_at = DateTimeField(auto_now_on_insert=True, auto_now_on_update=True)
    status = StringField(max_length=32, default=MessageStatusEnum('未发送').name)
    configure = JsonField()
    log = ListField(JsonField())
    is_active = BooleanField(default=True)


    @classmethod
    def validate_values(cls, dic, allow_cover=True):
        validated = super(Message, cls).validate_values(dic, allow_cover)
        schedule = validated['configure'].get('schedule', DefaultMessageSchedule)
        customized = validated['configure'].get('customized', [])
        if schedule == 'once':
            pass
        elif schedule == 'customized' and customized:
            sent_at = validated.get('sent_at')
            validated['next_sent_at'] = get_next_day(sent_at, customized, schedule)
        else:
            sent_at = validated.get('sent_at')
            validated['next_sent_at'] = get_next_day(sent_at, 1, schedule)
        return validated


    @staticmethod
    async def ir_cron():
        with open('/tmp/wodeshijie', 'a+') as f:
            for m in await Message.objects.find_all():
                f.write('%s \n' % m.title)
        return True







