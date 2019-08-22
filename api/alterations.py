# -*- coding: utf-8 -*-
# Filename: alterations
# Author: brayton
# Datetime: 2019-Jul-17 7:18 PM

import tornado
from tornado import gen
from tornado.web import HTTPError

from utils.token import token_manager
from handler import status
from handler.web import APIRequestHandler
from handler.exceptions import ParseError, ValidationError

from models.alterations import Alteration


class AlterationsHandler(APIRequestHandler):

    async def get(self, *args, **kwargs):
        alteration_id = kwargs.get('id')
        if alteration_id:
            alteration = await Alteration.objects.get(id=alteration_id)
            self.write_json({
                    'alterations': alteration.to_dict()
            })
        else:
            alterations = await Alteration.objects.find_all()
            self.write_json({
                'alterations': [alteration.to_dict() for alteration in alterations]
            })

    async def post(self, *args, **kwargs):

        print(f'The post data is {self.data}')
        if not self.data:
            raise ParseError('请提交正确的时间内容！')
        alteration = Alteration.from_dict(self.data)
        await alteration.save()

        self.write_json({
            'result': alteration.to_dict()
        })

    async def put(self, *args, **kwargs):
        alteration_id = kwargs.get('id')
        alteration = await Alteration.objects.get(id=alteration_id)
        if not alteration:
            raise ValidationError()
        validated = Alteration.validate_values(self.data)
        updated = Alteration.update(alteration, validated)
        await updated.save()
        self.write_json({
            'result': updated.to_dict()
        })

    async def delete(self, *args, **kwargs):
        alteration = await Alteration.objects.get(id=kwargs.get('id'))
        if not alteration:
            raise ValidationError()
        _id = alteration.to_dict().get('id')
        await alteration.delete()
        self.write_json({
            'result': _id
        })

