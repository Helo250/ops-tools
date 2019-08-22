# -*- coding: utf-8 -*-
# Filename: accounts
# Author: brayton
# Datetime: 2019-Jul-17 7:18 PM

import tornado
from tornado import gen
from tornado.web import HTTPError

from utils.token import token_manager
from handler import status
from handler.web import APIRequestHandler
from handler.exceptions import ParseError, ValidationError

from models.account import Account, ThirdPartyPlatform


class AccountsConfigHandler(APIRequestHandler):
    async def get(self, *args, **kwargs):
        platform_list = await ThirdPartyPlatform.objects.find_all()
        self.write_json({
            'thirdPartyPlatforms': [_platform.to_dict() for _platform in platform_list],
        })


class AccountsHandler(APIRequestHandler):

    async def get(self, *args, **kwargs):
        account_id = kwargs.get('id')
        if account_id:
            account = await Account.objects.filter(id=account_id).aggregate.fetch()
            print(account)
            self.write_json({
                'account': account
                # 'account': 'test'
            })
        else:
            accounts = await Account.objects.find_all()
            self.write_json({
                'accounts': [account.to_dict() for account in accounts]
            })

    async def post(self, *args, **kwargs):

        print(f'The post data is {self.data}')
        if not self.data:
            raise ParseError('请提交正确的时间内容！')
        account = Account.from_dict(self.data)
        await account.save()

        self.write_json({
            'result': account.to_dict()
        })

    async def put(self, *args, **kwargs):
        account_id = kwargs.get('id')
        account = await Account.objects.get(id=account_id)
        if not account:
            raise ValidationError()
        validated = Account.validate_values(self.data)
        updated = Account.update(account, validated)
        await updated.save()
        self.write_json({
            'result': updated.to_dict()
        })

    async def delete(self, *args, **kwargs):
        account = await Account.objects.delete(id=kwargs.get('id'))
        print('>>>>>>>>>>>>. delete account %s' % account)
        # if not account:
        #     raise ValidationError()
        # _id = account.to_dict().get('id')
        # await account.delete()
        self.write_json({
            'result': kwargs.get('id')
        })

