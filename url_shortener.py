#!/usr/bin/env python2.7
# coding:utf-8
from __future__ import print_function

import os
import _config as _cfg
import tornado.web
import tornado.ioloop
import tornado.log
import redis
from util import calc_expire_time, date_offset
from util import check_url, check_short_url, auth_check
import random
from collections import Counter
import logging
import time

logging.basicConfig(level=logging.DEBUG)

now = lambda : int(time.time())

__VERSION__ = '0.9.170222'

def authcheck(func):
    def _authcheck(self, *args, **kwargs):
        auth = self.request.headers.get('Authorization')
        if auth and auth_check(auth):
            return func(self, *args, **kwargs)
        else:
            self.set_header('WWW-Authenticate', 'Basic realm=tmr')
            self.set_status(status_code=401)
            self.on_finish()
    return _authcheck

class ControlSurlHandler(tornado.web.RequestHandler):
    @authcheck
    def post(self, *args):
        url = self.get_body_argument('url')
        suri = self.get_body_argument('short_url')
        suri = suri[len(_cfg.host):]
        expire = calc_expire_time(self.get_body_argument('expire'),
                         self.get_body_argument('expire_unit'))
        t, msg = check_url(url)
        if t == False:
            self.write(msg)

        t, msg = check_short_url(suri)
        if t == False:
            self.write(msg)

        rdb.add(suri, url, expire)
        self.write('ok')

    @authcheck
    def delete(self, suri):
        rdb.delete(suri)


class ControlRandomeStringHandler(tornado.web.RequestHandler):
    @authcheck
    def get(self):
        max_try_times = 10
        suri_list = rdb.list()
        suri_set = {x[0] for x in suri_list}
        while max_try_times:
            max_try_times -= 1
            uri = ''.join(random.sample(_cfg.URI_SEED, _cfg.short_uri_length))
            if uri not in suri_set:
                self.write(_cfg.host + uri)
                return
        self.write('Error: Please retry.')

class MainHandler(tornado.web.RequestHandler):
    @authcheck
    def get(self):
        sl = rdb.list()
        self.render('./templates/url_shortener.html', host=_cfg.host, url_set=sl)

class R302Handler(tornado.web.RequestHandler):
    def get(self, suri):
        url = rdb.get(suri)
        if not url:
            url = _cfg.miss_url
        self.redirect(url)

class OUSRedisDB(object):

    KN_SURI = _cfg.SURI_LIST_NAME

    def __init__(self, r):
        self.r = r

    def _list(self):
        return self.r.lrange(self.KN_SURI, 0, self.r.llen(self.KN_SURI))

    def list(self):
        suri_list = self._list()
        c = Counter(suri_list)
        if suri_list and len(c) != len(suri_list):
            logging.error('Suri_list_have_repeat_items')
            for suri, v in c.items():
                if v > 1:
                    logging.info('Delete_repeat_items')
                    self.r.lrem(self.KN_SURI, suri, v-1)
        suri_list = self._list()
        sl = []
        for idx, suri in enumerate(suri_list):
            url = self.r.get(suri)
            if url:
                ttl = self.r.ttl(suri)
                sl.append((suri, url, date_offset(ttl), idx, _cfg.host + suri))
            else:
                self.r.lrem(self.KN_SURI, suri, 1)
                logging.info('Surl_is_timeout')
        return sl

    def get(self, suri):
        url = self.r.get(suri)
        if not url:
            self.r.lrem(self.KN_SURI, suri, 1)
        return url

    def add(self, suri, url, expire):
        suri_list = self._list()
        assert suri not in suri_list
        self.r.rpush(self.KN_SURI, suri)
        self.r.set(suri, url, ex=expire)
        return True

    def delete(self, suri):
        return self.r.delete(suri), self.r.lrem(self.KN_SURI, suri)

if __name__ == '__main__':
    app = tornado.web.Application(
        [(r'/control/randomstring', ControlRandomeStringHandler),
         (r'/control/surl/(.*)', ControlSurlHandler),
         (r'/(\w+)', R302Handler),
         (r'/', MainHandler),
         # (r'/(assets/.*)', tornado.web.StaticFileHandler, {"path": '/home/gw1770/home/git/own-url-shortener/templates'}),
         ],
    )
    r = redis.Redis(*_cfg.redis_connect_cfg)
    rdb = OUSRedisDB(r)
    tornado.log.enable_pretty_logging()
    app.listen(_cfg.server_port)
    tornado.ioloop.IOLoop().instance().start()
