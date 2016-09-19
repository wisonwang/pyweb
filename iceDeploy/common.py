# -*- coding: utf-8 -*-

from uhaAppServer.services.base_service import init_mongo_db
import sys
# import traceback
import Ice
import uha
import json


def init(configFile="/opt/uhaService/ice-config/service.json"):
    with open(configFile) as f:
        config = json.load(f)
        mongoHost = config.get("mongo-host", "127.0.0.1")
        mongoPort = config.get("mongo-port", 27017)
        mongoMaxPoolSize = config.get("mongo-max-pool-size", 2000)
        init_mongo_db(mongoHost, mongoPort, mongoMaxPoolSize)


def createAndActivateAdapter(ic, adapterName, clazz):
    adapter = ic.createObjectAdapter(adapterName)
    properties = ic.getProperties()
    id = ic.stringToIdentity(properties.getProperty("Identity"))
    adapter.add(clazz(), id)
    adapter.activate()

init()
