# -*- coding: utf-8 -*-
# Filename: example
# Author: brayton
# Datetime: 2019-Jul-23 6:10 PM


from enum import Enum, unique
from datetime import datetime


DefaultMessageSchedule = 'once'
MaxDatetime = None


@unique
class EventLevelEnum(Enum):
    critical = '紧急'
    error = '错误'
    warning = '警告'
    informational = '通知'
    verbose = '冗长'


@unique
class EventStatusEnum(Enum):
    toStarted = '未开始'
    inProcessing = '处理中'
    isDone = '已完成'


@unique
class ScheduleIntervalEnum(Enum):
    once = '仅一次'
    daily = '每天'
    weekly = '每周'
    monthly = '每月'
    customized = '自定义'


@unique
class MediaEnum(Enum):
    sms = '短信'
    email = '邮件'
    mingChat = '明聊'


@unique
class MessageStatusEnum(Enum):
    to_send = '未发送'
    sent = '已发送'
    failed = '发送失败'


@unique
class ThirdPartyPlatformEnum(Enum):
    Aliyun = '阿里云'
    uCloud = 'uCloud'






