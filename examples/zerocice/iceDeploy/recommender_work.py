#!/usr/bin/env python
# -*- coding: utf-8;

from uhaAppServer.ice_proxy import IceProxyHelp
from uhaAppServer.apps.govpage.serializer import (govPageSerializer,
                                                  govPageMemberSerializer,
                                                  _getGovpageMembersInfo,
                                                  govPageMediaSerializer,
                                                  govpageService,
                                                  publishService,
                                                  userService)
from uhaAppServer.apps.user.serializer import userSerializer
from uhaAppServer.apps.publish.serializer import mediaSerializer
from uhaAppServer.apps.service_wrapper import deleteMediaCascade, deleteGovpageMembersCascade
from uhaAppServer.core.utils.simple_serialize import objectToDict, dictToObject, popDictNoneProperty
import uha
import json
import getopt
import sys
import time
import logging

logger = logging.getLogger("uha.recommender_work")


def recommenderService():
    return IceProxyHelp().recommender_service()

    
def generateGovpageData(govpage):
    try:
        d = govPageSerializer(objectToDict(govpage))
        data = uha.TRecommenderData()
        data.type = "UHA_TGOVPAGE"
        data.docString = json.dumps(d)
        recommenderService().updateData(data)
        
        deleteGovpageMembersCascade(d.get("id"))
    except Exception as e:
        logger.error(e)
        

def resolveGovPageError(page):
    m = govpageService().getOneByFilter(
                uha.TGovPageMember(),
                json.dumps({"pageId": page.id,
                            "role": "creator",
                            "isValid": {"$in": [True, False]}}))
    print m
    if m:
        page.creator = m.userId
        print govpageService().updateById(page)
        
        
def govPageWork():
    query = {"limit": 10,
             "filter": {"isValid": {"$in": [True, False]}},
             "sort": [{"id": -1}],
             "offset": 0}
    ret = govpageService().query(uha.TGovPage(), json.dumps(query))
    while (ret.offset < ret.total):
        for i in ret.result:
            generateGovpageData(i)
        query["offset"] += 10
        ret = govpageService().query(uha.TGovPage(), json.dumps(query))


def govpageCreatorError():
    query = {"limit": 10,
             "sort": [{"id": -1}],
             "filter": {"creator": 0, "isValid": {"$in": [True, False]}},
             "offset": 0}
    ret = govpageService().query(uha.TGovPage(), json.dumps(query))
    while (ret.offset < ret.total):
        for i in ret.result:
            resolveGovPageError(i)
        query["offset"] += 10
        ret = govpageService().query(uha.TGovPage(), json.dumps(query))

        
def generateMediaData(media):
    try:
        d = mediaSerializer(objectToDict(media))
        data = uha.TRecommenderData()
        if not d["isValid"]:
            deleteMediaCascade(d.get("id"))
        data.type = "UHA_TMEDIA"
        data.docString = json.dumps(d)
        recommenderService().updateData(data)
    except Exception as e:
        logger.error(e)
        

def mediaWork():
    query = {"limit": 10,
             "filter": {"isValid": {"$in": [True, False]}},
             "sort": [{"id": -1}],
             "offset": 0}
    ret = publishService().queryMedia(json.dumps(query))
    while (ret.offset < ret.total):
        for i in ret.result:
            generateMediaData(i)
        query["offset"] += 10
        ret = govpageService().query(uha.TGovPage(), json.dumps(query))


def generateUserData(user):
    try:
        d = userSerializer(objectToDict(user))
        data = uha.TRecommenderData()
        data.type = "UHA_TUSER"
        data.docString = json.dumps(d)
        recommenderService().updateData(data)
    except Exception as e:
        logger.error(e)
    
            
def userWork():
    query = {"limit": 10,
             "sort": [{"id": -1}],
             "offset": 0}
    ret = userService().query(uha.TUser(), json.dumps(query))
    while (ret.offset < ret.total):
        for i in ret.result:
            generateUserData(i)
        query["offset"] += 10
        ret = userService().query(uha.TUser(), json.dumps(query))

        
def actionWork():
    query = {"limit": 10,
             "filter": {
                 "actionType": "govpage_publish_media"
             },
             "sort": [{"id": -1}],
             "offset": 0}
    ret = publishService().query(uha.TAction(), json.dumps(query))
    while (ret.offset < ret.total):
        for i in ret.result:
            if i.pageId == 0:
                m = govpageService().getById(uha.TGovPageMedia(), i.targetId)
                if m:
                    i.pageId = m.pageId
                    i = publishService().updateById(i)
                    print i
        query["offset"] += 10
        ret = userService().query(uha.TUser(), json.dumps(query))
        
    
def usage():
    print '''
NAME
    description
Usage
    python recommender_work.py [options]
'''[1:-1]


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    file = ""

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            file = a
        else:
            assert False, "unhandled option"

    while(True):
        time.sleep(60)
        userWork()
        mediaWork()
        govPageWork()
