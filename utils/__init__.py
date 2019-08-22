# coding: utf-8
import six
from importlib import import_module
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure

weekday_ranking = {
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6,
    'Sunday': 7
}


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        module_path, class_name = val.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


def uncapitalize(s):
    return s[:1].lower() + s[1:] if s else ''


def snake2camel(name):
    return ''.join(
        map(lambda x: x.capitalize(), name.split('_'))
    )


def get_weekday(_datetime):
    assert isinstance(_datetime, datetime)
    return _datetime.isoweekday()


def get_next_day(_datetime: datetime, interval: (list, int) = 1, schedule: str = 'days') -> datetime:
    assert isinstance(interval, (list, int))
    if isinstance(interval, list):
        rank = get_weekday(_datetime)
        for s in interval:
            tmp = weekday_ranking[s] - rank
            if tmp > 0:
                days = tmp
                break
        else:
            days = 7
        delta = {'days': days}
    else:
        if schedule == 'months':
            try:
                next_date = _datetime.replace(month=_datetime.month + interval)
            except ValueError:
                if _datetime.month == 12:
                    next_date = _datetime.replace(year=_datetime.year, month=1)
                else:
                    next_date = get_next_day(_datetime, interval+1, schedule)
            return next_date
        delta = {schedule: interval}
    return _datetime + timedelta(**delta)


def detect_mongo(**config):
    test_config = dict(
        **config,
        serverselectiontimeoutms=500
    )
    print(f'>>>>>>{test_config}')
    try:
        # The ismaster command is cheap and does not require auth.
        MongoClient(**test_config).admin.command('ismaster')
        return True
    except ConnectionFailure:
        return False



if __name__ == '__main__':
    # now = datetime.now()
    # print(type(now))
    # schedule = ['Monday', 'Thursday']
    # print(get_next_day(now, schedule))
    # print(get_next_day(now, 4))
    # print(get_next_day(now, 2, 'months'))
    print()

