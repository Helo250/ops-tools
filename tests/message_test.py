# -*- coding: utf-8 -*-
# Filename: message
# Author: brayton
# Datetime: 2019-Jul-23 4:56 PM

import json

from api.messages import MessagesHandler
from . import WebTestCase


class MessagesHTTPTest(WebTestCase):

    def get_handlers(self):
        return [
            ('/messages', MessagesHandler),
            (r'/messages/(?P<id>[\w\d]+)', MessagesHandler)
        ]

    # def test_get_messages(self):
    #     response = self.fetch('/messages')
    #     print(f'>>>>>>>>>>>>{response.body}')
    #     self.assertEqual(response.code, 200)

    def test_get_configures(self):
        response = self.fetch('/messages/configures')
        result = self.process_body(response.body)
        print(f'>>>>>>>>>{result}')
        self.assertEqual(response.code, 200)

    def test_get_one_message(self):
        response = self.fetch('/messages/5d3983f157045c4ac77662e8')
        result = response.body.decode()
        print(f'>>>>>>>>>>>>>>>> {result}')
        # self.assertEqual()

    # def test_update_one_message(self):
    #     data = {
    #         'messageName': '测试名',
    #     }
    #     response = self.fetch(
    #         '/messages/5d3983f157045c4ac77662e8',
    #         method='POST',
    #         body=json.dumps(data).encode()
    #     )
    #     result = self.process_body(response.body)
    #     print(f'The response is {result}')

    def test_post_customized_messages(self):
        body = dict(messageTitle='测试', messageContent='通知内容我也不知道', messageComment='勉强写一下',
                    messageSentAt='2019-08-20 17:48:18',
                    messageSentFrom={'cmdb_uid': 2523, 'username': 'shenwei', 'email': 'shenwei@huored.com',
                                     'mobile': '18551643757'}, messageSentBy=['email', 'sms'],
                    messageSentTo=[{'cmdb_uid': '1853', 'username': 'biaomei', 'mobile': '13456146050'},
                                   {'cmdb_uid': '1849', 'username': '柯熊', 'mobile': '13454010912'},
                                   {'cmdb_uid': '1560', 'username': '包中', 'mobile': '13456119014'}],
                    messageConfigure={'schedule': 'customized', 'customized': ['Monday', 'Tuesday']})
        resp = self.fetch('/messages', method='POST', body=json.dumps(body).encode())
        result = resp.body.decode()
        print(f'The response is {result}')
        self.assertEqual(resp.code, 200)

    def test_post_once_message(self):
        data = dict(messageTitle='测试', messageContent='通知内容我也不知道', messageComment='勉强写一下',
                    messageSentAt='2019-08-20 17:48:18',
                    messageSentFrom={'cmdb_uid': 2523, 'username': 'shenwei', 'email': 'shenwei@huored.com',
                                     'mobile': '18551643757'}, messageSentBy=['email', 'sms'],
                    messageSentTo=[{'cmdb_uid': '1853', 'username': 'biaomei', 'mobile': '13456146050'},
                                   {'cmdb_uid': '1849', 'username': '柯熊', 'mobile': '13454010912'},
                                   {'cmdb_uid': '1560', 'username': '包中', 'mobile': '13456119014'}],
                    messageConfigure={'schedule': 'once', 'customized': []})
        body = self.prepare_body(data)
        resp = self.fetch('/messages', method='POST', body=body)
        result = resp.body.decode()
        print(f'The response is {result}')
        self.assertEqual(resp.code, 200)
