# -*- coding: utf-8 -*-
# Filename: utils
# Author: brayton
# Datetime: 2019-Jul-17 6:15 PM

import re
from motorengine import BaseField


class MobileField(BaseField):
    MOBILE_REGEX = re.compile(r"^1[35678]\d{9}$")

    def validate(self, value):
        if value is None:
            return True

        is_mobile = MobileField.MOBILE_REGEX.match(value)
        return is_mobile


if __name__ == '__main__':
    from datetime import datetime
    print(datetime.fromtimestamp(1563969300.530))
