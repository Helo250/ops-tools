# -*- coding: utf-8 -*-
# Filename: event
# Author: brayton
# Datetime: 2019-Jul-23 4:56 PM

from api.events import EventsHandler
from . import WebTestCase


class EventsHTTPTest(WebTestCase):

    def get_handlers(self):
        return [
            ('/events', EventsHandler),
            (r'/events/(?P<id>[\w\d]+)', EventsHandler)
        ]

    # def test_get_events(self):
    #     response = self.fetch('/events')
    #     print(f'>>>>>>>>>>>>{response.body}')
    #     self.assertEqual(response.code, 200)


    def test_get_configures(self):
        response = self.fetch('/events/configures')
        result = self.process_body(response.body)
        print(f'>>>>>>>>>{result}')
        self.assertEqual(response.code, 200)

    def test_get_one_event(self):
        response = self.fetch('/events/5d3983f157045c4ac77662e8')
        print(f'>>>>>>>>>>>>>>>> {response.body}')
        # self.assertEqual()

    def test_update_one_event(self):
        data = {
            'eventName': '测试名',
        }
        body = self.prepare_body(data)
        response = self.fetch(
            '/events/5d3983f157045c4ac77662e8',
            method='POST',
            body=body
        )
        result = self.process_body(response.body)
        print(f'The response is {result}')


    # def test_post_events(self):
    #     body = {
    #         'name': 'nihao',
    #         'status': 1,
    #         'level': 2,
    #     }
    #     resp = self.fetch('/events/1', method='POST', body=json.dumps(body).encode())
    #     print(f'The response is {resp.body}')
