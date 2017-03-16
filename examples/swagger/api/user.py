# -*- coding: utf-8 -*-

import logging

import flask
import json


def make_response(ret, code):
    res = flask.make_response(ret, code)
    res.headers['Content-Type'] = 'application/json'
    return res


def register(registerInfo):
    return make_response(registerInfo, 200)


def login(loginInfo):
    d = json.loads(loginInfo)
    password = d.get("password")
    phone = d.get("phone")
    logging.info("{0}{1}".format(phone, password))
    return make_response(json.dumps({"code": 200}), 200)


def thirdPartLogin(thirdPartLoginInfo):
    return "test"

