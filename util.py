#!/usr/bin/env python2.7
# coding:utf-8

import datetime
import re
import requests
import base64
from _config import host, auth_userlist

HTTP_CODE_OK = [2,3]

def calc_expire_time(n, unit):
    if unit == 'h':
        return int(n) * 60 * 60
    elif unit == 'd':
        return int(n) * 60 * 60 * 24

def date_offset(offset_second=0):
    d = datetime.datetime.now() + datetime.timedelta(seconds=offset_second)
    return d.strftime('%m-%d %H:%M')

def check_url(url):
    re_url = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if not re_url.match(url):
        return False, 'Error: %s is not url, please check.' % url
    resp = requests.head(url)
    if resp.status_code / 100 not in HTTP_CODE_OK:
        return False, 'Error: %s Can`t visit, please check.' % url
    return True, 0

def check_short_url(url):
    re_url= re.compile('^[a-zA-Z0-9]+$')
    if not re_url.match(url):
        return False, 'Error: short url:%s not legitimacy' % url
    return True, 0

def auth_check(auth_string):
    method, auth = auth_string.split(' ')
    assert method == 'Basic'
    auth = base64.b64decode(auth)
    return not auth_userlist or auth in auth_userlist
