# -*- coding: utf-8 -*-
# from decorator import decorate


def singleton(cls, *args1, **kw1):
    """
    decorator singleton implement.
    """
    instances = {}
    # print args1, kw1

    def _singleton(*args, **kw):
        if cls not in instances:
            # print args, kw
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton
