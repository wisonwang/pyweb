#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2016 ZeroC, Inc. All rights reserved.
#
# **********************************************************************

import sys
# import traceback
import Ice
import IceGrid
import uha


class Client(Ice.Application):
    def run(self, args):
        if len(args) > 1:
            print(self.appName() + ": too many arguments")
            return 1

        userService = None
        publishService = None
        try:
            query = IceGrid.QueryPrx.checkedCast(
                self.communicator().stringToProxy(
                    "UhaIceGrid/Query"))
            userService = uha.UserServicePrx.checkedCast(
                query.findObjectByType("::uha::UserService"))
            publishService = uha.PublishServicePrx.checkedCast(
                query.findObjectByType("::uha::PublishService"))
        except Exception as e:
            print e

        print userService.query(uha.TUser(), '{"limit": 1}')
        print publishService.query(uha.TComment(), '{"limit": 1}')
        if not userService:
            print(self.appName()
                  + ": couldn't find a `::uha::UserService' object.")
            return 1
        return 0

app = Client()
app.main(sys.argv, "/opt/uhaService/ice-config/config.client")
#sys.exit(app.main(sys.argv, "/opt/uhaService/ice-config/config.client"))
