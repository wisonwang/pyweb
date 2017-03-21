#!/usr/bin/env python
# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- vim:fenc=utf-8:ft=python:et:sw=4:ts=4:sts=4

import getopt
import sys
import pyweb.openapi.app as app
from flask_oauthlib.provider import OAuth2Provider
# from flask_oauthlib.provider import OAuth1Provider
from pyweb.utils.logger import init_logger
import os


oauth = OAuth2Provider()


def usage():
    print '''
NAME
    description
Usage
    python program.py [options]
'''[1:-1]
    

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    file = ""
    init_logger("SwaggerServer")
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            file = os.path.realpath(a)
        else:
            assert False, "unhandled option"
            
    static_folder = file+"templates"
    
    app.run_server(specification_base_dir=file,
                   template_folder=static_folder)



