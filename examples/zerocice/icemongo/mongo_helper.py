# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pymongo.collection import ReturnDocument
from simple_serialize import objectToDict, dictToObject
from singleton import singleton
import types
import time
import json


@singleton
class MongoHelper(object):
    
    def __init__(self, host="127.0.0.1", port=27017, maxPoolSize=2000, **kw):
        # print host, port, maxPoolSize
        self.client = MongoClient(host=host,
                               port=port,
                               maxPoolSize=maxPoolSize)

    def get_mongo_client(self, dbName):
        return self.client.get_database(dbName)


    def get_collection_name(self, entityType):
        """
        约定数据库表名
        """
        typeName = str(entityType)
        typeName = typeName[typeName.find("'")+1:]
        typeName = typeName[:typeName.find("'")]
    
        return typeName.replace(".", "_").upper()


    def get_increment_id(self, idName="id-name"):
        """
        mongodb default not support global unique increment id,
        so use a document to store unique id of the collection
        param c:colection name
        """
        db = self.get_mongo_client("counter")
        co = db["counters"]
        p = co.find_one({"_id": idName})
        if not p:
            co.insert_one({"_id": idName, "seq": 100000})

        p = co.find_one_and_update(
            {'_id': idName},
            {'$inc': {'seq': 1}}, return_document=ReturnDocument.AFTER)

        return p["seq"]


    def set_doc_create_time(self, doc):
        doc["createTime"] = long(time.time())


    def set_doc_update_time(self, doc):
        doc["updateTime"] = long(time.time())


    def common_query(self, c, query):
        # TODO: deprecated
        d = json.loads(query)
        filters = d.get("filter", {})
        offset = d.get("offset", 0)
        limit = d.get("limit", 100)
        sort = d.get("sort", [])

        if isinstance(sort, types.DictionaryType):
            ss = []
            for k, v in sort.items():
                ss.append((k, v))
                sort = ss
        cursor = c.find(filter=filters, skip=offset, limit=limit, sort=sort)
        r = dict()
        r["total"] = cursor.count()
        r["offset"] = offset
        sets = []
        for c in cursor:
            sets.append(c)
        r["result"] = sets
        if r["total"] <= r["offset"]:
            r["result"] = []
        return r


def getMongoHelper(**kw):
    return MongoHelper(**kw)

    
class BaseDao:
    def __init__(self, db, entityClz):
        """
        db:mongo db client obj
        collection: mongo collection name
        entityClz:mapping entity class
        """
        self.db = db
        self.collectionName = getMongoHelper().get_collection_name(entityClz)
        self.c = db[self.collectionName]
        self.clz = entityClz

    def create(self, entity):
        if isinstance(entity, self.clz):
            entity.id = get_increment_id(self.collectionName)
            d = objectToDict(entity)
            d["_id"] = d.get("id")
            d["isValid"] = True
            set_doc_create_time(d)
            set_doc_update_time(d)
            self.c.save(d)
            d = self.c.find_one({"id": entity.id})
            return dictToObject(d, self.clz())
        else:
            return None
            
    def update(self, entity):
        d = objectToDict(entity)
        getMongoHelper().set_doc_update_time(d)
        d["isValid"] = True
        d = self.c.find_one_and_update({"id": entity.id},
                                       {"$set": d},
                                       return_document=ReturnDocument.AFTER)
        if d:
            return dictToObject(d, self.clz())
        else:
            # TODO: logger
            return None

    def get(self, id):
        d = self.c.find_one({"id": id})
        if d:
            return dictToObject(d, self.clz())
        else:
            # TODO: logger
            return None

    def delete(self, id):
        return self.c.find_one_and_update({"id":  id},
                                          {'$set':  {"isValid":  False}},
                                          return_document=ReturnDocument.AFTER)

    def query(self, filter={},
              offset=0, limit=100, sort=[]):

        ss = []
        for s in sort:
            if isinstance(s, types.DictionaryType):
                for k, v in s.items():
                    ss.append((k, v))
            else:
                ss.append(s)
        sort = ss
        if len(sort) == 0:
            sort = [("id", -1)]
        
        if "isValid" not in filter.keys():
            filter["isValid"] = True
        cursor = self.c.find(filter=filter,
                             skip=offset, limit=limit, sort=sort)
        
        r = dict()
        r["total"] = cursor.count()
        r["offset"] = offset
        sets = []
        for c in cursor:
            sets.append(dictToObject(c, self.clz()))
        r["result"] = sets
        if r["total"] <= r["offset"]:
            r["result"] = []
        return r

    def batchUpdate(self, filter={},
                    update={}):
        if "isValid" in filter.keys():
            filter["isValid"] = True
        result = self.c.update_many(filter,
                                    update)
        r = dict()
        r["total"] = result.matched_count
        r["offset"] = 0
        sets = []
        for c in result.raw_result:
            sets.append(dictToObject(c, self.clz()))
        r["result"] = sets
        return r
        