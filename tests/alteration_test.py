# -*- coding: utf-8 -*-
# Filename: alteration_test
# Author: brayton
# Datetime: 2019-Aug-14 8:11 PM

from api.alterations import AlterationsHandler
from . import WebTestCase


class AlterationsTest(WebTestCase):
    def get_handlers(self):
        return [
            [r'/alterations', AlterationsHandler],
            [r'/alterations/(?P<id>[\w\d]{24})', AlterationsHandler],
        ]

    def test_post_alterations(self):
        data = dict(
            alterationTitle="测试",
            alterationEffect="测试影响",
            alterationExecuteAt="2019-08-14 20:09:27",
            alterationProduct="我的世界",
            alterationReason="测试原因",
            alterationSentAt="2019-08-14 20:09:27",
            alterationSentTo=[
                {'cmdb_uid': '1853', 'username': 'biaomei', 'mobile': '13456146050'},
                {'cmdb_uid': '1849', 'username': '柯熊', 'mobile': '13454010912'}
            ],
            alterationSentBy=["email"]
        )
        body = self.prepare_body(data)
        resp = self.fetch('/alterations', method='POST', body=body)
        result = resp.body.decode()
        print(f'The response is {result}')
        self.assertEqual(resp.code, 200)
