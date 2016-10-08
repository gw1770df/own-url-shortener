#!/usr/bin/env python2.7
# coding:utf-8

from flask import Flask, request, Response
from functools import wraps

app = Flask(__name__)

CONTROL_FUN_NAME = set(['add'])

@app.route('/control', methods=['POST'])
def control_hub():
    fun_name = request.args.get('fn', None)
    assert fun_name, 'fun_name error'
    assert fun_name in CONTROL_FUN_NAME, 'fun_name value error'
    if fun_name == 'add':
        post_data = dict(request.form)
        print post_data
        post_get = lambda x : post_data[x][0].encode('utf-8')
        url = post_get('url')
        expire = post_get('expire')
        print url
        print expire
    # except Exception, e:
    #     return Response('Error:\n%s' % e.message, 500)
    return 'ok'

if __name__ == "__main__":
    app.run(port=11801,
            debug=True)

