#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
import time
from uhaAppServer.core.global_settings import global_init, GlobalSetting
from uhaAppServer.core.utils.simple_serialize import dictToObject, objectToDict
from uhaAppServer.apps.publish.serializer import mediaSerializer
from uhaAppServer.apps.user.serializer import userSerializer
from uhaAppServer.apps.govpage.serializer import govPageSerializer
from uhaAppServer.core.utils.push import noticeAll, noticeByAlias
from uhaAppServer.core.decorators import cached
from uhaAppServer.ice_proxy import IceProxyHelp
import uha
import json
import copy
import logging
import sys


reload(sys)
sys.setdefaultencoding("utf-8")

global_init(json.load(open("/opt/uhaService/app-config.json")))


def get_global_settings():
    return GlobalSetting()


class AlertTemplate:
    activity_join = "{userName} 等申请参加 {activityName} 活动"
    activity_confirm = "{userName}, 您申请的 {activityName} 活动已经报名成功,请准时参加."
    activity_reject = "{userName}, 您申请的 {activityName} 活动未申核通过."
    activity_warning = "{userName}, 您申请的 {activityName} 活动将于 {startTime} 开始,请准时参加."
    activity_exit = "您已经退出{activityName}活动，如果已经支付，支付款会在一周以内退回."


def NoticeService():
    return IceProxyHelp().notice_service()


def PublishService():
    return IceProxyHelp().publish_service()

    
def UserService():
    return IceProxyHelp().user_service()


def GovpageService():
    return IceProxyHelp().govpage_service()

logger = logging.getLogger("uha.rabitmqWork")


@cached(3600)
def cachedSendMessage(m):
    if get_global_settings().isDev():
        pass
    try:
        if m.dispatchTo == 0:
            noticeAll(m.alert)
        else:
            noticeByAlias(m.alert, str(m.dispatchTo))
    except Exception as e:
        logger.exception(e)


def cachedDispatchMessage(m):
    if m.dispatchTo != 0:
        cachedSendMessage(m)
    else:
        if not get_global_settings().isDev():
            noticeAll(m.alert)
    return NoticeService().dispatchMessage(m)


def getGovpageMembersByRole(pageId, roles=["admin", "creator"]):
    query = {
        "filter": {
            "pageId": pageId,
            "role": {"$in": roles}
        },
        "limit": 100
    }
    ret = GovpageService().query(uha.TGovPageMember(), json.dumps(query))
    return ret


def getMediaById(mediaId):
    query = {
        "filter": {
            "id": mediaId,
            "isValid": {"$in": [False, True]}
        },
        "limit": 1
    }
    ret = PublishService().queryMedia(json.dumps(query))
    if ret.total > 0:
        return ret.result[0]
    return None

    
def isMatchType(t, types):
    for i in types:
        if t.find(i) == 0:
            return True
    return False


def testDispatchMessage(id):
    m = NoticeService().getById(uha.TNoticeMessage(), id)
    if m:
        m = dictToObject(objectToDict(m), uha.TDispatchMessage())
        m = dispatchMessage(m)
        logger.info(m)
    else:
        logger.info("not valid id %s" % id)


def dispatchActivityStartWarnning(m):
    content = json.loads(m.content)
    mediaId = content.get("activityId")
    mediaInfo = mediaSerializer(objectToDict(getMediaById(mediaId)))
    userInfo = userSerializer(
        objectToDict(
            UserService().getById(uha.TUser(), content.get("userId"))))
    content = {}
    
    content["usersInfo"] = [userInfo]
    content["mediaInfo"] = mediaInfo
    m.content = json.dumps(content)
    offset = 0
    total = 0
    query = {
        "filter": {"activityId": mediaId}
    }
    while offset >= total:
        ret = PublishService().query(uha.TParticipantInfo(),
                                     json.dumps(query))
        offset = ret.offset
        total = ret.total
        m.type = "user.activity.attention.start.warning"
        startTime = time.strftime("%m月%d日%H时%M分",
                                  time.gmtime(
                                      mediaInfo["activityInfo"]["startTime"]))
        for r in ret.result:
            m.dispatchTo = r.userId
            m.alert = AlertTemplate.activity_warning.format(
                userName=userInfo["name"],
                activityName=mediaInfo["title"], startTime=startTime)
            cachedDispatchMessage(m)
        

def dealWithActivityMessage(dispatchMessage):
    content = json.loads(dispatchMessage.content)
    mediaId = content.get("activityId")
    mediaInfo = mediaSerializer(objectToDict(getMediaById(mediaId)))
    userInfo = userSerializer(
        objectToDict(
            UserService().getById(uha.TUser(), content.get("userId"))))

    content["mediaInfo"] = mediaInfo
    content["userInfo"] = userInfo
    dispatchMessage.content = json.dumps(content)

    dispatchMessage.dispatchTo = mediaInfo["promulgatorId"]
   
    dispatchMessage = cachedDispatchMessage(dispatchMessage)
    if dispatchMessage.type == "user.activity.join":
        filter = {"type": "user.activity.attention.join",
                  "status": "new",
                  "dispatchTo": mediaInfo["promulgatorId"]}
        m = NoticeService().getOneByFilter(
            uha.TDispatchMessage(), json.dumps(filter))

        if m and json.loads(m.content).get("activityId"):
            m.alert = AlertTemplate.activity_join.format(
                userName=userInfo["name"],
                activityName=mediaInfo["title"])
            content = json.loads(m.content)
            content["usersInfo"].append(userInfo)
            m.content = json.dumps(content)
            NoticeService().updateById(m)
        else:
            m = copy.deepcopy(dispatchMessage)
            content = {}
            content["usersInfo"] = [userInfo]
            content["mediaInfo"] = mediaInfo
            m.content = json.dumps(content)
            m.type = "user.activity.attention.join"
            m.alert = AlertTemplate.activity_join.format(
                userName=userInfo["name"],
                activityName=mediaInfo["title"])
            cachedDispatchMessage(m)
    elif dispatchMessage.type == "user.activity.confirm.join":
        m = copy.deepcopy(dispatchMessage)
        content = {}
        content["usersInfo"] = [userInfo]
        content["mediaInfo"] = mediaInfo
        m.content = json.dumps(content)
        m.dispatchTo = userInfo["id"]
        m.alert = AlertTemplate.activity_confirm.format(
            userName=userInfo["name"], activityName=mediaInfo["title"])
        m.type = "user.activity.attention.confirm.join"
        cachedDispatchMessage(m)
    elif dispatchMessage.type == "user.activity.reject.join":
        m = copy.deepcopy(dispatchMessage)
        content = {}
        content["usersInfo"] = [userInfo]
        content["mediaInfo"] = mediaInfo
        m.content = json.dumps(content)
        m.dispatchTo = userInfo["id"]
        m.alert = AlertTemplate.activity_reject.format(
            userName=userInfo["name"], activityName=mediaInfo["title"])
        m.type = "user.activity.attention.reject.join"
        cachedDispatchMessage(m)
    elif "user.activity.start.warning" == dispatchMessage.type:
        m = copy.deepcopy(dispatchMessage)
        dispatchActivityStartWarnning(m)
    elif "user.activity.exit" == dispatchMessage.type:
        m = copy.deepcopy(dispatchMessage)
        content = {}
        content["usersInfo"] = [userInfo]
        content["mediaInfo"] = mediaInfo
        m.content = json.dumps(content)
        m.dispatchTo = userInfo["id"]
        m.alert = AlertTemplate.activity_exit.format(
            activityName=mediaInfo["title"])
        m.type = "user.activity.attention.exit"
        cachedDispatchMessage(m)


def dispatchMessage(dispatchMessage):
    if dispatchMessage.type in ["user.media.comment",
                                "user.media.vote"]:
        content = json.loads(dispatchMessage.content)
        mediaId = content.get("targetId")
        mediaInfo = getMediaById(mediaId)
        userInfo = UserService().getById(uha.TUser(), content.get("userId"))

        content["mediaInfo"] = mediaSerializer(objectToDict(mediaInfo))
        content["userInfo"] = userSerializer(objectToDict(userInfo))
        dispatchMessage.content = json.dumps(content)

        dispatchMessage.dispatchTo = mediaInfo.promulgatorId
        if dispatchMessage.type == "user.media.comment":
            dispatchMessage.alert = "%s 评论了 %s" % (userInfo.name, mediaInfo.title)
        elif dispatchMessage.type == "user.media.vote":
            dispatchMessage.alert = "%s 赞了 %s" % (userInfo.name, mediaInfo.title)
        dispatchMessage = cachedDispatchMessage(dispatchMessage)
    elif isMatchType(dispatchMessage.type, ["user.activity"]):
        content = json.loads(dispatchMessage.content)
        mediaId = content.get("activityId")
        mediaInfo = getMediaById(mediaId)
        userInfo = UserService().getById(uha.TUser(), content.get("userId"))

        content["mediaInfo"] = mediaSerializer(objectToDict(mediaInfo))
        content["userInfo"] = userSerializer(objectToDict(userInfo))
        dispatchMessage.content = json.dumps(content)
        
        dispatchMessage.dispatchTo = mediaInfo.promulgatorId
        if dispatchMessage.type == "user.activity.join":
            dispatchMessage.alert = "%s 申请加入了 %s 活动" % (userInfo.name, mediaInfo.title)
        elif dispatchMessage.type == "user.activity.exit":
            dispatchMessage.alert = "%s 退出了 %s 活动" % (userInfo.name, mediaInfo.title)
        dispatchMessage = cachedDispatchMessage(dispatchMessage)
        dealWithActivityMessage(dispatchMessage)

    elif isMatchType(dispatchMessage.type, ["govpage.report.media",
                                            "govpage.contribute",
                                            "govpage.confirm.contribute"]):
        content = json.loads(dispatchMessage.content)
        mediaId = content.get("sourceMediaId")
        pageId = content.get("pageId")
        mediaInfo = getMediaById(mediaId)
        userInfo = UserService().getById(uha.TUser(), mediaInfo.promulgatorId)

        content["mediaInfo"] = mediaSerializer(objectToDict(mediaInfo))
        content["userInfo"] = userSerializer(objectToDict(userInfo))
        dispatchMessage.content = json.dumps(content)

        if dispatchMessage.type.find("govpage.contribute") == 0:
            dispatchMessage.alert = "%s 申请投稿 %s" % (userInfo.name, mediaInfo.title)
        elif dispatchMessage.type == "govpage.report.media":
            dispatchMessage.alert = "%s 举报了 %s" % (userInfo.name, mediaInfo.title)
        if isMatchType(dispatchMessage.type, ["govpage.confirm.contribute"]):
            dispatchMessage.dispatchTo = dispatchMessage.senderId
            dispatchMessage = cachedDispatchMessage(dispatchMessage)
        roles = ["admin", "creator"]
        ms = getGovpageMembersByRole(pageId, roles)
        logger.info(ms)
        for i in ms.result:
            dispatchMessage.dispatchTo = i.userId
            dispatchMessage = cachedDispatchMessage(dispatchMessage)
            logger.info(dispatchMessage)

    elif dispatchMessage.type in ["govpage.apply.join",
                                  "govpage.apply.admin"]:
        content = json.loads(dispatchMessage.content)
        pageId = content.get("pageId")
        pageInfo = GovpageService().getById(uha.TGovPage(), pageId)
        userInfo = UserService().getById(uha.TUser(), dispatchMessage.senderId)
        
        content["pageInfo"] = govPageSerializer(objectToDict(pageInfo))
        content["userInfo"] = userSerializer(objectToDict(userInfo))
        dispatchMessage.content = json.dumps(content)

        if dispatchMessage.type == "govpage.apply.join":
            dispatchMessage.alert = "%s 申请加入 %s" % (userInfo.name, pageInfo.name)
        elif dispatchMessage.type == "govpage.apply.admin":
            dispatchMessage.alert = "%s 申请加入 %s" % (userInfo.name, pageInfo.name)
        admins = getGovpageMembersByRole(pageId)
        for i in admins.result:
            dispatchMessage.dispatchTo = i.userId
            dispatchMessage = cachedDispatchMessage(dispatchMessage)
    else:
        dispatchMessage = cachedDispatchMessage(dispatchMessage)
    return dispatchMessage

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='message_queue', durable=True)


def callback(ch, method, properties, body):
    logger.info("Received %s" % body)
    d = json.loads(body)
    m = dictToObject(d, uha.TDispatchMessage())
    m.sourceMessageId = d["id"]
    try:
        dispatchMessage(m)
        logger.info("%s  Done" % body)
    except Exception as e:
        logger.error(e, exc_info=1)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='message_queue')


def deferWorkCallback(ch, method, properties, body):
    logger.info("Received %s" % body)
    try:
        exec body
    except Exception as e:
        logger.error(e, exc_info=1)
    logger.info("%s  Done" % body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.queue_declare(queue='deferWork_queue', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(deferWorkCallback,
                      queue='deferWork_queue')


channel.start_consuming()

