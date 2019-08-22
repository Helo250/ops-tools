# -*- coding: utf-8 -*-
# Filename: alteration_test
# Author: brayton
# Datetime: 2019-Aug-14 8:11 PM

from api.accounts import AccountsHandler
from . import WebTestCase


class AccountsTest(WebTestCase):
    def get_handlers(self):
        return [
            [r'/accounts', AccountsHandler],
            [r'/accounts/(?P<id>[\w\d]{24})', AccountsHandler],
        ]

    def test_get_accounts(self):
        response = self.fetch('/accounts')
        print(f'>>>>>>>>>>>>>>>> {response.body}')

    def test_get_string_id_account(self):
        response = self.fetch('/accounts/5d5cfd9457045c6d5aef0438')
        print(response.body.decode())
        self.assertEqual(response.code, 200)

    # def test_get_bson_id_account(self):
    #     response = self.fe

    def test_post_accounts(self):
        data = dict(
            accountAccess={
                'users': [
                    {'cmdb_uid': '1853', 'username': 'biaomei', 'mobile': '13456146050'},
                    {'cmdb_uid': '1849', 'username': '柯熊', 'mobile': '13454010912'}
                ],
                'group': []
                },
            accountAccount="shenwei@huored.com",
            accountName="测试",
            accountPassword="SCkbmy7ukuyHfK6",
            accountPlatform="aliyun",
            accountUrl="",
            accountAdaptor=''
        )
        body = self.prepare_body(data)
        resp = self.fetch('/accounts', method='POST', body=body)
        result = resp.body.decode()
        print(f'The response is {result}')
        self.assertEqual(resp.code, 200)

    def __str__(self):
        return self.name
