#!/usr/bin/env python
# coding:utf-8

from motorengine import connect
from tornado import gen, ioloop
from settings import MONGODB
from models.event import Event, EventLevel, EventStatus
from models.message import NotifySchedule, NotifyMedia
from models.account import ThirdPartyPlatform
from data.example import (
    EventLevelEnum, EventStatusEnum, MediaEnum,
    ScheduleIntervalEnum, ThirdPartyPlatformEnum)


async def init_event_level():
    for event in await EventLevel.objects.find_all():
        await event.delete()

    for level in EventLevelEnum:
        await EventLevel(code=level.name, name=level.value).save()


async def init_event_status():
    for status in await EventStatus.objects.find_all():
        await status.delete()
    for status in EventStatusEnum:
        await EventStatus(code=status.name, name=status.value).save()


async def init_message_schedule():
    for schedule in ScheduleIntervalEnum:
        await NotifySchedule(code=schedule.name, name=schedule.value).save()


async def init_message_media():
    for media in MediaEnum:
        await NotifyMedia(code=media.name, name=media.value).save()


async def init_third_part_platform():
    for platform in ThirdPartyPlatformEnum:
        await ThirdPartyPlatform(code=platform.name, name=platform.value).save()


async def init_db():
    # await init_event_status()
    # await init_event_level()
    await init_message_media()
    await init_message_schedule()
    await init_third_part_platform()

    io_loop.stop()


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.instance()
    connect(MONGODB.name, host=MONGODB.host, port=MONGODB.port, io_loop=io_loop)

    io_loop.add_timeout(1, init_db)
    io_loop.start()

