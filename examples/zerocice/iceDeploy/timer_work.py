#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
from uhaAppServer.core.global_settings import global_init
from uhaAppServer.core.utils.simple_serialize import dictToObject, objectToDict
from uhaAppServer.apps.publish.serializer import mediaSerializer
from uhaAppServer.apps.user.serializer import userSerializer
from uhaAppServer.apps.govpage.serializer import govPageSerializer
from uhaAppServer.ice_proxy import IceProxyHelp
import uha
import json
import time, os, sched 
import logging

global_init(json.load(open("/opt/uhaService/app-config.json")))
logger = logging.getLogger("uha.timer.work")

schedule = sched.scheduler(time.time, time.sleep)


def perform_command(callback, inc):
    schedule.enter(inc, 0, perform_command, (callback, inc))
    callback()


def timming_exe(callback, inc=60):
    schedule.enter(inc, 0, perform_command, (callback, inc))
    schedule.run()


def echoMessage():
    print "hello world"


def NoticeService():
    return IceProxyHelp().notice_service()


def PublishService():
    return IceProxyHelp().publish_service()

    
def UserService():
    return IceProxyHelp().user_service()


def GovpageService():
    return IceProxyHelp().govpage_service()




