# coding:utf-8

from url import urls
import tornado.web

from settings import SERVER

app = tornado.web.Application(
    handlers=urls,
    template_path=SERVER.template_path,
    static_path=SERVER.static_path,
    debug=SERVER.debug,
    cookie_secret=SERVER.cookie_secret,
    allow_remote_access=SERVER.allow_remote_access,
    default_handler_class=SERVER.default_handler_class,
    autoreload=False
)
