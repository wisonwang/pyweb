# -*- coding: utf-8 -*-
import types
import cPickle as pickle
# import pickle
import logging
logger = logging.getLogger("uha.core.utils.simple_serialize")


def objectDumps(obj):
    return pickle.dumps(obj)


def objectLoads(string):
    return pickle.loads(string)


def objectToDict(obj):
    """
    """
    if obj is None:
        return {}
    if type(obj) in [types.IntType,
                     types.StringType,
                     types.LongType,
                     types.FloatType,
                     types.DictType,
                     types.NoneType]:
        return obj
    val = dict()
    for k, v in obj.__dict__.items():
        if isinstance(v, types.ClassType):
            val[k] = objectToDict(v)
        elif isinstance(v, types.ListType):
            val[k] = [objectToDict(o) for o in v]
        else:
            val[k] = v
    return val


def dictToObject(d, obj):
    """
    """
    try:
        if d is None:
            return None
        for k, v in d.items():
            # print k,v
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj
    except Exception as e:
        logger.info(e)
    return None


def popDictNoneProperty(d):
    for k, v in d.items():
        if v is None:
            d.pop(k)
        if isinstance(v, types.DictType):
            popDictNoneProperty(v)
    return d

    
def popDictPropertyByKeys(d, keys=[]):
    for k in keys:
        if k in d.keys():
            d.pop(k)
    return d

    
def arrayUpdate(old, add):
    for t in add:
        if t not in old:
            old.append(t)

    return old


def arrayRemove(old, remove):
    for t in remove:
        if t in old:
            old.remove(t)
            old = arrayRemove(old, [t])
    return old


def getQueryFromDict(d):
    query = {}
    query["filter"] = d.get("filter", {})
    query["limit"] = d.get("limit", 10)
    query["offset"] = d.get("offset", 0)
    query["sort"] = d.get("sort", [])
    return query
    
