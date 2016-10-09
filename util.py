#!/usr/bin/env python2.7
# coding:utf-8

import datetime

def calc_expire_time(n, unit):
    if unit == 'h':
        return int(n) * 60 * 60
    elif unit == 'd':
        return int(n) * 60 * 60 * 24

def date_offset(offset_second=0):
    d = datetime.datetime.now() + datetime.timedelta(seconds=offset_second)
    return d.strftime('%m-%d %H:%M')
