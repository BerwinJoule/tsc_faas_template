#!/usr/bin/env python
import os
import json
import logging
from waitress import serve
from flask import Flask, request
from function import handler

app = Flask(__name__)


class Event:
    def __init__(self):
        self.body = request.get_data()
        self.headers = request.headers
        self.method = request.method
        self.query = request.args
        self.path = request.path
        self.json = request.get_json()
        self.form = request.form
        self.files = request.files


class Context:
    def __init__(self):
        self.hostname = os.getenv('HOSTNAME', 'localhost')


def format_status_code(resp):
    if 'statusCode' in resp:
        return resp['statusCode']
    return 200


def format_mime_type(resp):
    if 'mimetype' in resp:
        return resp['statusCode']
    else:
        return "application/json"


def format_body(resp):
    if 'body' not in resp:
        return ""
    elif type(resp['body']) in (dict, list):
        return json.dumps(resp['body'])
    else:
        return resp['body']


def format_headers(resp):
    if 'headers' not in resp:
        return []
    elif type(resp['headers']) == dict:
        headers = []
        for key in resp['headers'].keys():
            header_tuple = (key, resp['headers'][key])
            headers.append(header_tuple)
        return headers

    return resp['headers']


def format_response(resp):
    if resp is None:
        return '', 200, 'text/html'
    else:
        statuscode = format_status_code(resp)
        body = format_body(resp)
        headers = format_headers(resp)
        return body, statuscode, headers


@app.route('/', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def call_handler(path):
    event = Event()
    context = Context()
    response_data = handler.handle(event, context)
    resp = format_response(response_data)
    return resp


if __name__ == '__main__':
    app.debug = True
    applogger = app.logger

    file_handler = logging.FileHandler('FaasLog.log')
    file_handler.setLevel(logging.DEBUG)

    serve(app, host='0.0.0.0', port=5000)
