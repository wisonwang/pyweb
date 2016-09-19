#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2016 ZeroC, Inc. All rights reserved.
#
# **********************************************************************
from uhaAppServer.services.user.server import UserServiceI
from uhaAppServer.services.publish.server import PublishServiceI
from uhaAppServer.services.notice.server import NoticeServiceI
from uhaAppServer.services.govpage.server import GovPageServiceI
from uhaAppServer.services.pay.server import PayServiceI
from uhaAppServer.services.recommender.server import RecommenderServiceI
from common import createAndActivateAdapter
import Ice
import uha
import sys

_ServiceI = {
    "UserServiceI": UserServiceI,
    "PublishServiceI": PublishServiceI,
    "GovPageServiceI": GovPageServiceI,
    "NoticeServiceI": NoticeServiceI,
    "PayServiceI": PayServiceI,
    "RecommenderServiceI": RecommenderServiceI
}


class Server(Ice.Application):
    def run(self, args):
        if len(args) > 1:
            print(self.appName() + ": too many arguments")
            return 1
        ServerId = self.appName()
        createAndActivateAdapter(self.communicator(),
                                 ServerId, _ServiceI.get(ServerId+"I"))

        self.communicator().waitForShutdown()
        return 0

app = Server()
sys.exit(app.main(sys.argv))
