# -*- coding: utf-8 -*-
# Filename: events
# Author: brayton
# Datetime: 2019-Jul-17 7:18 PM

import tornado
from tornado import gen
from tornado.web import HTTPError

from utils.token import token_manager
from handler import status
from handler.web import APIRequestHandler
from handler.exceptions import ParseError, ValidationError

from models.event import Event, EventLevel, EventStatus


class EventsConfigHandler(APIRequestHandler):
    async def get(self, *args, **kwargs):
        status_list = await EventStatus.objects.find_all()
        level_list = await EventLevel.objects.find_all()
        self.write_json({
            'eventStatus': [_status.to_dict() for _status in status_list],
            'eventLevel': [_level.to_dict() for _level in level_list]
        })


class EventsHandler(APIRequestHandler):

    async def get(self, *args, **kwargs):
        event_id = kwargs.get('id')
        if event_id:
            event = await Event.objects.get(id=event_id)
            self.write_json({
                'event': event.to_dict()
            })
        else:
            events = await Event.objects.find_all()
            self.write_json({
                'events': [event.to_dict() for event in events]
            })

    async def post(self, *args, **kwargs):

        print(f'The post data is {self.data}')
        if not self.data:
            raise ParseError('请提交正确的时间内容！')
        event = Event.from_dict(self.data)
        await event.save()

        self.write_json({
            'result': event.to_dict()
        })

    async def put(self, *args, **kwargs):
        event_id = kwargs.get('id')
        event = await Event.objects.get(id=event_id)
        if not event:
            raise ValidationError()
        validated = Event.validate_values(self.data)
        updated = Event.update(event, validated)
        await updated.save()
        self.write_json({
            'result': updated.to_dict()
        })

    async def delete(self, *args, **kwargs):
        event = await Event.objects.get(id=kwargs.get('id'))
        if not event:
            raise ValidationError()
        _id = event.to_dict().get('id')
        await event.delete()
        self.write_json({
            'result': _id
        })

