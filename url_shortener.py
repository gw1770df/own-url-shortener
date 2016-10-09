#!/usr/bin/env python2.7
# coding:utf-8

from flask import Flask, request, Response, render_template, redirect
from functools import wraps
import redis
import _config
from util import calc_expire_time, date_offset
from util import check_url, check_short_url
import random
import string
from collections import Counter
import requests

app = Flask(__name__)

r = redis.Redis(*_config.redis_connect_cfg)

URI_SEED = ''
if 'lower_letters' in _config.short_uri_includ:
    URI_SEED += string.ascii_lowercase
if 'upper_letters' in _config.short_uri_includ:
    URI_SEED += string.ascii_uppercase
if 'digits' in _config.short_uri_includ:
    URI_SEED += string.digits

CONTROL_FUN_NAME = set(['add', 'random', 'rem'])


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if get_current_user_role() not in roles:
                return error_response()
            return f(*args, **kwargs)
        return wrapped
    return wrapper

@app.route('/control', methods=['GET', 'POST'])
def control_hub():
    fun_name = request.args.get('fn', None)
    assert fun_name, 'fun_name error'
    assert fun_name in CONTROL_FUN_NAME, 'fun_name value error'
    if fun_name == 'add':
        post_data = dict(request.form)
        post_get = lambda x : post_data[x][0].encode('utf-8')
        url = post_get('url')
        short_url = post_get('short_url')
        expire = post_get('expire')
        expire_unit = post_get('expire_unit')
        expire_time = calc_expire_time(expire, expire_unit)
        short_uri = short_url[len(_config.host):]
        t, msg = check_url(url)
        if t == False:
            return msg

        t, msg = check_short_url(short_url)
        if t == False:
            return msg

        __url = r.get(short_uri)
        if __url != None:
            return 'Error: short url exist, Please retry.'
        r.set(short_uri, url)
        r.expire(short_uri, expire_time)
        r.rpush(_config.uri_list_name, short_uri)
        return 'ok'

    elif fun_name == 'random':
        max_try_times = 10
        while max_try_times:
            uri = ''.join(random.sample(URI_SEED, 4))
            if r.get(uri) == None:
                print _config.host + uri
                return _config.host + uri
            max_try_times -= 1
        return 'Error: Please retry.'

    elif fun_name == 'rem':
        post_data = dict(request.form)
        post_get = lambda x : post_data[x][0].encode('utf-8')
        short_url = post_get('delete')
        uri = short_url[len(_config.host):]
        r.delete(uri)
        r.lrem(_config.uri_list_name, uri)
        return 'ok'
    # except Exception, e:
    #     return Response('Error:\n%s' % e.message, 500)
    # return 'ok'

@app.route('/')
def root():
    uri_list = r.lrange(_config.uri_list_name, 0, r.llen(_config.uri_list_name))
    if len(uri_list) != len(set(uri_list)):
        counter_uri = Counter(uri_list)
        r_uri = [(k, v) for k,v in counter_uri.items() if v>=2]
        pipe = r.pipeline()
        reduce(lambda pipe,v:pipe.lrem(_config.uri_list_name, v[0], v[1]-1), r_uri, pipe)
        pipe.execute()
        uri_list = r.lrange(_config.uri_list_name, 0, r.llen(_config.uri_list_name))
    su = []
    for idx, uri in enumerate(uri_list):
        url = r.get(uri)
        short_url = _config.host + uri
        date = date_offset(r.ttl(uri))
        su.append((url, short_url, date, idx))
    print su
    return render_template('url_shortener.html', host = _config.host, url_set=su)

@app.route('/<uri>')
def red(uri):
    url = r.get(uri)
    if url == None:
        url = _config.miss_url
    return redirect(url, code=302)


if __name__ == "__main__":
    app.run(port=11801,
            debug=False)

