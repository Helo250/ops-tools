# coding:utf-8

from tornado.options import options

from api.events import EventsHandler, EventsConfigHandler
from api.messages import MessagesHandler, MessagesConfigHandler
from api.alterations import AlterationsHandler
from api.accounts import AccountsHandler, AccountsConfigHandler

urls = [
    [r'/events/configures', EventsConfigHandler],
    [r'/events', EventsHandler],
    [r'/events/(?P<id>[\w\d]{24})', EventsHandler],
    [r'/messages/configures', MessagesConfigHandler],
    [r'/messages', MessagesHandler],
    [r'/messages/(?P<id>[\w\d]{24})', MessagesHandler],
    [r'/alterations', AlterationsHandler],
    [r'/alterations/(?P<id>[\w\d]{24})', AlterationsHandler],
    [r'/accounts', AccountsHandler],
    [r'/accounts/(?P<id>[\w\d]{24})', AccountsHandler],
    [r'/accounts/configures', AccountsConfigHandler],
    # [r'.*', APIDefaultHandler],
]

# Add subpath to urls
for u in urls:
    u[0] = options.subpath + u[0]
