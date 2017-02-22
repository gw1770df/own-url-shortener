#!/usr/bin/env python2.7
# coding:utf-8

import string

# 监听端口
server_port = 11081

# debug模式开关
server_debug = False

# 用于url缩短的域名 要以'/'结尾
host = 'http://s.g1770.cc/'

# 当uri没有对应关系时，跳转到的地址A
miss_url = 'https://word.gw1770df.cc'

# redis连接信息
redis_connect_cfg = ('127.0.0.1', 6379, 0)

# redis uri_list 变量名称
SURI_LIST_NAME = 'SURI_DICT'
SURI_SET_NAME = 'SURI_SET'

# 账户信息配置支持多个用户格式为 用户名:密码
# 但用户配置信息不分离。
auth_userlist = ['admin:admin']


# 随机uri包含的字符 可选项：
# 'lower_letters' 小写字母
# 'upper_letters' 大写字母
# 'digits'        数字
short_uri_includ = ['lower_letters', 'digits']

# 随机uri长度
short_uri_length = 4

# 没用
user_list = {'admin': 'admin'}

URI_SEED = ''
if 'lower_letters' in short_uri_includ:
    URI_SEED += string.ascii_lowercase
if 'upper_letters' in short_uri_includ:
    URI_SEED += string.ascii_uppercase
if 'digits' in short_uri_includ:
    URI_SEED += string.digitsz
