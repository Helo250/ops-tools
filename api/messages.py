# -*- coding: utf-8 -*-
# Filename: message
# Author: brayton
# Datetime: 2019-Jul-17 7:18 PM

import tornado
from tornado import gen
from tornado.web import HTTPError

from utils.token import token_manager
from handler import status
from handler.web import APIRequestHandler
from handler.exceptions import ParseError, ValidationError

from models.message import Message, NotifyMedia, NotifySchedule


class MessagesConfigHandler(APIRequestHandler):
    async def get(self, *args, **kwargs):
        notify_medias = await NotifyMedia.objects.find_all()
        notify_schedules = await NotifySchedule.objects.find_all()
        self.write_json({
            'notifyMedia': [t.to_dict() for t in notify_medias],
            'notifySchedule': [s.to_dict() for s in notify_schedules]
        })


class MessagesHandler(APIRequestHandler):

    async def get(self, *args, **kwargs):
        message_id = kwargs.get('id')
        if message_id:
            message = await Message.objects.get(id=message_id)
            if not message:
                raise ValidationError('未知的ID')
            self.write_json({
                'message': message.to_dict()
            })
        else:
            messages = await Message.objects.find_all()
            self.write_json({
                'messages': [message.to_dict() for message in messages]
            })

    async def post(self, *args, **kwargs):

        print(f'The post data is {self.data}')
        if not self.data:
            raise ParseError('请提交正确的时间内容！')
        message = Message.from_dict(self.data)
        await message.save()

        self.write_json({
            'result': message.to_dict()
        })

    async def put(self, *args, **kwargs):
        message_id = kwargs.get('id')
        message = await Message.objects.get(id=message_id)
        if not message:
            raise ValidationError()
        validated = Message.validate_values(self.data)
        updated = Message.update(message, validated)
        await updated.save()
        self.write_json({
            'result': updated.to_dict()
        })

    async def delete(self, *args, **kwargs):
        message = await Message.objects.get(id=kwargs.get('id'))
        if not message:
            raise ValidationError()
        _id = message.to_dict().get('id')
        await message.delete()
        self.write_json({
            'result': _id
        })

