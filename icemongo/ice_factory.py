# -*- coding: utf-8 -*-
from uhaAppServer.core.singleton import singleton
import sys
import Ice
import IceGrid
import os
from logging import getLogger

logger = getLogger('uha.core.ice_factory')

os.environ["ICE_CONFIG"] = "/opt/uhaService/ice-config/config.client"


@singleton
class IceFactory():
    """
    wrapper ice common functions.
    """
    _ic = None

    def __init__(self, config=dict(), *args, **kwargs):
        "ice factory init"
        # TODO: xxx
        self._ic = Ice.initialize(sys.argv)

    def getIceProxy(
            self, ProxyType, proxyTypeName):

        proxy = None
        try:
            query = IceGrid.QueryPrx.checkedCast(
                self._ic.stringToProxy("UhaIceGrid/Query"))
            proxy = ProxyType.checkedCast(
                query.findObjectByType(proxyTypeName))
        except Exception as e:
            print e
            logger.error(e)
        return proxy

    def wait(self):
        self._ic.waitForShutdown()
        self.destroy_ic()

    def destroy_ic(self):
        if self._ic:
            try:
                self._ic.destroy()
            except Exception, e:
                global logger
                logger.info("%s" % e)

