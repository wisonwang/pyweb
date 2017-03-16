# -*- coding: utf-8 -*-

import logging


def init_logger(appName):
    fmt = '[%(asctime)s] [{AppName}] [%(levelname)s] [%(funcName)s] [%(filename)s:%(lineno)d] - %(message)s'.format(AppName=appName)
    formatter = logging.Formatter(fmt)
    logger = logging.getLogger()
    
    logger.setLevel(logging.INFO)
    if len(logger.handlers) == 0:
        myhandler = logging.StreamHandler()  # writes to stderr
        logger.addHandler(myhandler)
    for h in logger.handlers:
        h.setFormatter(formatter)
    logger.info("set logging")
        