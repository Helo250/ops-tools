# -*- coding: utf-8 -*-
# Filename: setting
# Author: brayton
# Datetime: 2019-Jul-18 10:45 AM

from collections import defaultdict
import config

from utils import perform_import

DEFAULT_IMPORT_STRINGS = {
    'default_handler_class'
}


class Settings(object):
    """
    A settings object, allow user get special namespace settings
    """
    def __init__(self, user_settings, defaults=None, import_strings=None):
        self._user_settings = self.__check_user_settings(user_settings)
        self._defaults = defaults or defaultdict(None)
        self._import_strings = import_strings or DEFAULT_IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        return self._user_settings

    def keys(self):
        return self._user_settings.keys()

    def __getitem__(self, item):
        return self._user_settings[item]

    # def __iter__(self):
    #     return iter(self.user_settings)

    def __getattr__(self, attr):
        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self._defaults[attr]
        if val and attr in self._import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, setting):
        return setting


MONGODB = Settings(config.MONGODB)
JWT = Settings(config.JWT_AUTH)
SERVER = Settings(config.APPLICATION)

