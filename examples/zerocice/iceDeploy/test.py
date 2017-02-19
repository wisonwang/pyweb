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
from uhaAppServer.apps.user.serializer import userBaseSerializer as userSerializer
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


def _getMediaById(mediaId):
    query = {
        "filter": {
            "id": mediaId,
            "isValid": {"$in": [False, True]}
        },
        "limit": 1
    }
    ret = publishService().queryMedia(json.dumps(query))
    if ret.total > 0:
        return ret.result[0]
    return None


temp_value = u"<h2 style=\"text-align: center;\">\u90a3\u4e9b\u4ee5\u670b\u53cb\u540d\u4e49\u76f8\u5904\uff0c\u5374\u559c\u6b22\u7740\u5bf9\u65b9\u7684\u4eba\u4eec</h2><p style=\"\"><span style=\"font-size: 14px;\">\u770b\u4e86\u300a\u9646\u579a\u77e5\u9a6c\u4fd0\u300b\uff0c\u8d77\u521d\u8bb2\u7684\u662f\u4e00\u4e2a\u201c\u9752\u6885\u7af9\u9a6c\uff0c\u4e24\u5c0f\u65e0\u731c\u201d\u7684\u6545\u4e8b\uff1b&nbsp; <img src=\"http://7xq98z.com2.z0.glb.qiniucdn.com/spaceme_web/1468985638438\" alt=\"Image\" height=\"366.85\" width=\"550\">\u540e\u6765\u8bb2\u7684\u662f\u4e00\u4e2a\u201c\u53cb\u8fbe\u4ee5\u4e0a\uff0c\u604b\u4eba\u672a\u6ee1\u201d\u7684\u6545\u4e8b\uff1b</span><span style=\"font-size: 14px;\">&nbsp; <img src=\"http://7xq98z.com2.z0.glb.qiniucdn.com/spaceme_web/1468985655980\" alt=\"Image\" height=\"366.6666666666667\" width=\"550\"> </span><font>\u6700\u540e\u8bb2\u7684\u662f\u4e00\u4e2a\u201c\u591a\u60c5\u5df2\u4e45\uff0c\u6df1\u60c5\u4e0d\u8d1f\u201d\u7684\u6545\u4e8b</font><span style=\"font-size: 14px;\"><img src=\"http://7xq98z.com2.z0.glb.qiniucdn.com/spaceme_web/1468985661295\" alt=\"Image\" height=\"366.85\" width=\"550\"></span><span style=\"font-size: 14px;\">\u5728\u8fd9\u4e09\u4e2a\u6545\u4e8b\u91cc\uff0c\u6211\u770b\u5230\u4e86\u65e5\u4e45\u89c1\u4eba\u5fc3\uff0c\u5374\u4e0d\u89c1\u9646\u579a\u77e5\u9a6c\u4fd0\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u4ece\u5e7c\u513f\u56ed\u8d77\u9752\u6885\u7af9\u9a6c\u5230\u6700\u540e\u7684\u6df1\u60c5\u4e0d\u8d1f\uff0c\u8fd9\u5bf9CP\u76f4\u523031\u5c81\u90fd\u6ca1\u6709\u8868\u767d\u8fc7\uff0c\u539f\u56e0\u5c31\u662f\u7537\u4e3b\u60a3\u6709\u4e25\u91cd\u7684\u8868\u767d\u65e0\u529b\u75c7\uff0c\u6240\u4ee5\u9009\u62e9\u4e86\u201c\u966a\u4f34\u662f\u6700\u957f\u60c5\u7684\u544a\u767d\u201d\u3002\u53ef\u4ed6\u4e0d\u660e\u767d\u8fd9\u53e5\u8bdd\u7684\u6838\u5fc3\u5e94\u8be5\u662f\u201c\u544a\u767d\u201d\uff0c\u4e0d\u662f\u201c\u966a\u4f34\u201d\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u9646\u579a\u771f\u5e94\u8be5\u53cd\u590d\u53bb\u542c\u542c\u6881\u9759\u8339\u7684\u300a\u52c7\u6c14\u300b\u3002\u5e7c\u513f\u56ed\u65f6\u671f\u7684\u7ae5\u771f\uff0c\u5927\u5b66\u65f6\u671f\u7684\u521d\u543b\u3001\u6bd5\u4e1a\u89c1\u9762\u7684\u8868\u767d\u3001\u5df4\u585e\u7f57\u90a3\u540c\u5e8a\u2026\u2026\u6bcf\u4e00\u4e2a\u5173\u952e\u6027\u7684\u8282\u70b9\u9646\u579a\u603b\u662f\u540e\u9000\u4e00\u6b65\uff0c\u9634\u5dee\u9633\u9519\u3002\u5728\u5e7c\u513f\u56ed\u65f6\u671f\u540c\u5e8a\u65f6\u5019\u90fd\u77e5\u9053\u52a8\u624b\u52a8\u811a\u7684\u9646\u579a\uff0c30\u597d\u51e0\u7684\u65f6\u5019\u716e\u719f\u7684\u9e2d\u5b50\u9001\u5230\u5634\u8fb9\u4e86\uff0c\u7adf\u7136\u5634\u90fd\u4e0d\u77e5\u9053\u5f20\u4e00\u4e0b\uff01\u6574\u573a\u5305\u8d1d\u5c14\u5145\u5206\u5851\u9020\u4e86\u4e00\u4e2a\u5b8c\u7f8e\u5907\u80ce\u5e94\u5177\u6709\u7684\u6240\u6709\u54c1\u8d28\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u5f71\u7247\u6700\u540e\u9009\u7528\u4e86\u5f20\u7231\u73b2\u7684\u4e00\u53e5\u8bdd\u63cf\u8ff0\u4e86\u9646\u579a\u4e0e\u9a6c\u4fd0\u7684\u7231\u60c5\uff1a\u201c\u7231\u53ef\u4ee5\u8ba9\u4f60\u9a84\u50b2\u5982\u70c8\u65e5\uff0c\u4e5f\u53ef\u4ee5\u8ba9\u6211\u5351\u5fae\u5982\u5c18\u571f\u201d \u8868\u793a\u9646\u579a\u8868\u767d\u65e0\u529b\u5b8c\u5168\u662f\u56e0\u4e3a\u81ea\u5351\uff0c\u53ef\u4ed6\u5c82\u6b62\u5351\u5fae\u5982\u5c18\u571f\uff0c\u8fd9\u5c18\u571f\u751a\u81f3\u5df2\u7ecf\u628a\u4ed6\u57cb\u4e86\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u66fe\u7ecf\u6211\u4e5f\u559c\u6b22\u8fc7\u4e00\u4e2a\u5973\u751f\uff0c\u6211\u4eec\u4e00\u76f4\u4ee5\u670b\u53cb\u76f8\u5904\u3002\u5979\u806a\u660e\uff0c\u6f02\u4eae\uff0c\u5bb6\u5883\u6bb7\u5b9e\uff0c\u8000\u773c\u5230\u6211\u5b8c\u5168\u6ca1\u6709\u52c7\u6c14\u5411\u5979\u8868\u767d\u3002\u5728\u4e34\u8fd1\u5927\u5b66\u6bd5\u4e1a\u7684\u90a3\u4e2a\u591c\u665a\uff0c\u5728\u64cd\u573a\u4e0a\u5979\u8ddf\u6211\u8bf4\uff1a\u5230\u4e86\u4e09\u5341\u5c81\u7684\u65f6\u5019\uff0c\u4f60\u6ca1\u7ed3\u5a5a\uff0c\u6211\u4e5f\u6ca1\u627e\u5230\u5408\u9002\u7684\uff0c\u6211\u4eec\u4e24\u5c31\u5728\u4e00\u8d77\u5427\u3002\u90a3\u662f\u4e2a\u55a7\u56a3\u7684\u591c\u665a\uff0c\u6709\u665a\u98ce\uff0c\u6709\u6708\u5149\u3002\u6211\u8bf4\u597d\u554a\uff0c\u4f46\u5fc3\u91cc\u660e\u767d\u7684\u5f88\u3002\u6211\u559c\u6b22\u5979\uff0c\u6b23\u8d4f\u5979\uff0c\u4f46\u662f\u5373\u4fbf\u5230\u4e8630\u5c81\u6211\u4eec\u5e76\u4e0d\u4f1a\u771f\u7684\u8c08\u604b\u7231\u3002\u4e00\u5ea6\u6211\u628a\u8fd9\u5f52\u4e3a\u81ea\u5351\uff0c\u6162\u6162\u7684\u5c31\u6539\u53d8\u4e86\u60f3\u6cd5\uff0c\u5176\u5b9e\u6211\u4e0d\u9002\u5408\u5979\uff0c\u5979\u4e5f\u771f\u7684\u4e0d\u9002\u5408\u6211\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u4ed6\u4eec\u4e24\u4e2a\u7684\u6545\u4e8b\u662f\u9001\u7ed9\u90a3\u4e9b\u4ee5\u670b\u53cb\u540d\u4e49\u76f8\u5904\uff0c\u5374\u559c\u6b22\u7740\u5bf9\u65b9\u7684\u4eba\u4eec\uff0c\u9001\u7ed9\u90a3\u4e9b\u5e74\u4e5f\u66fe\u75f4\u5fc3\u5984\u60f3\u3001\u5929\u5929yy\u7684\u6211\u4eec\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u5982\u679c\u8bf4\u201c\u7231\u4e00\u4e2a\u4eba\u7b2c\u4e00\u611f\u89c9\u662f\u914d\u4e0d\u4e0a\u5979\u201d\u8fd9\u7b97\u662f\u4e00\u79cd\u7231\u60c5\u7684\u8bdd\uff0c\u90a3\u8d75\u5954\u548c\u65b9\u7070\u7070\u7684\u5851\u9020\u7684\u5c31\u662f\u201c\u7231\u4e00\u4e2a\u4eba\u9a6c\u4e0a\u5c31\u8981\u4e0a\u4e86\u5979\u201d\u7684\u7231\u60c5\u3002\u4ed6\u4eec\u5355\u8eab\u65f6\u662f\u7978\u5bb3\u4eba\u95f4\uff0c\u5728\u4e00\u8d77\u662f\u4e3a\u6c11\u9664\u5bb3\u3002\u4ed6\u4fe9\u4e00\u8a00\u4e0d\u5408\u5c31\u641e\u5230\u4e86\u4e00\u8d77\uff0c\u5982\u540c\u8131\u7f30\u7684\u91ce\u9a6c\u4e00\u6837\u7b56\u9a6c\u5954\u817e\u3002\u7231\u60c5\u771f\u7684\u4e5f\u53ef\u4ee5\u662f\u8fd9\u6837\uff0c\u5f88\u76f4\u63a5\uff0c\u7231\u60c5\u9700\u8981\u884c\u52a8\uff0c\u800c\u4ed6\u4eec\u5c31\u662f\u6700\u597d\u7684\u884c\u52a8\u6d3e\u3002\u4ed6\u4eec\u4fe9\u7684\u6545\u4e8b\u9001\u7ed9\u626d\u626d\u634f\u634f\uff0c\u6ca1\u6709\u52c7\u6c14\u8868\u767d\u7684\u6211\u4eec\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u8fd9\u90e8\u7535\u5f71\u4e5f\u8bb8\u4e0e\u6211\u4eec\u6240\u5904\u7684\u73b0\u5b9e\u4e0d\u540c\uff0c\u5728\u73b0\u5728\u7684\u5feb\u8282\u594f\u7684\u90fd\u5e02\u751f\u6d3b\u4e2d\uff0c\u4e0d\u4f1a\u5b58\u5728\u201c\u4e09\u5341\u5c81\u4e4b\u65e5\uff0c\u4f60\u82e5\u672a\u5ac1\uff0c\u6211\u82e5\u672a\u5a36\uff0c\u505a\u4f60\u7684\u6258\u5e95\u53ef\u597d\uff1f\u201d\u8fd9\u7c7b\u60c5\u8bdd\u6216\u662f\u50bb\u8bdd\uff0c\u4e5f\u4e0d\u4f1a\u51fa\u73b0\u4e00\u8a00\u4e0d\u5408\u5c31\u7ed3\u5a5a\u8fd8\u5f7c\u6b64\u76f8\u7231\u7684\u611f\u60c5\u3002\u4f46\u662fwho care\u5462\uff1f\u91cd\u8981\u7684\u662f\uff0c\u6211\u770b\u5230\u4e86\u6211\u4eec\u7684\u5f71\u5b50\u3002</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">\u6700\u540e\u6211\u60f3\u8bf4\uff0c\u6587\u7ae0\u8fd8\u662f\u61c2\u7231\u60c5\u7684\u5427\u3002</span></p><p style=\"text-align: justify;\"></p><hr><p style=\"text-align: justify;\"><b><span style=\"font-size: 14px;\">\u53c2\u4e0e\u65b9\u5f0f</span></b></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">1\u3001\u5173\u6ce8\u201c\u5c0f\u9504\u5934\u201d\u516c\u5171\u4e3b\u9875\uff0c\u5728\u672c\u6b21\u6d3b\u52a8\u4e0b\u65b9\u53c2\u4e0e\u5e73\u8bba\uff0c\u8bf4\u8bf4\u4f60\u60f3\u5bf9\u300a\u9646\u579a\u77e5\u9a6c\u4fd0\u300b\u8bf4\u7684\u8bdd</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">2\u3001\u6211\u4eec\u5c06\u968f\u673a\u62bd\u53d610\u540d\u7c89\u4e1d\u9001\u4e0a\u300a\u9646\u579a\u77e5\u9a6c\u4fd0\u300b\u7535\u5f71\u5168\u56fd\u901a\u5151\u7535\u5f71\u7968\u4e00\u5f20</span></p><p style=\"text-align: justify;\"><span style=\"font-size: 14px;\">ps\uff1a\u70b9\u8d5e\u6570\u8d8a\u591a\u7684\u8bc4\u8bba\u4e2d\u5956\u51e0\u7387\u8d8a\u5927\u54e6<br></span></p>"


def updateContent():
    i = _getMediaById(101428)
    print i
    i.content[0].value = temp_value
    print publishService().updateMedia(i)

targetPages = {# 
    u"知更社区":	u"已移交",  # 只有一个
    u"不止读书":	u"魏小河",  # 100246, 100491
    u"多茉": u"多茉",  # 100282(100253), 
    u"译林出版社": u"译林出版社",  # 100117 100497
    u"左右青春":	u"Clown",  # done
    u"小锄头": u"严莫",   # 100116
    u"独艺无二":	u"艺仔",  # 100249,100494
    u"曲玮玮": u"曲玮玮",  # 100250, 100518
    u"S奥森跑团": u"滔来.涛去",  # none
    u"爱健身骑车的晓丹": u"晓丹",  # 100120 100439
    u"篮球热视频": u"篮球视频",  # 100265, 100440
    u"天津BMX李晓刚": u"BMX李晓刚",  # 100113 100466
    u"詹姆斯贴吧": u"詹姆斯吧",  # 100126, 100476
    u"库里中文网": u"Curry你懂的",  # 100125, 100498
    u"健身潮人":	u"健身潮人",  # 100122, 100490
    u"电影公会":	u"姜小瑁",   # 100094, 100475
    u"牛二杯-北京攀岩":	u"攀岩户外",  # 100287, 100509
    u"天津BMX李晓刚":	u"李晓刚BMX",  # 100113, 100466
    u"四季市集":	u"菁",  # 100192 100524
    u"摄影文一":	u"摄影文一",  # 100112, 100505
    u"民谣故事":	u"民谣故事",   # 100211,100312
    u"余文乐可乐团":	u"余文乐可乐团",  # none 
    u"果酱音乐":	u"果酱音乐",  # 100080 100535
    u"宁波灯塔音乐现场":	u"左宅",  # 100127 100473
    u"兰州城市之光":	u"兰州城市之光",  # 100128 none ---
    u"周杰伦歌迷网":	u"周杰伦歌迷网"  # 100129 100536
}

u"兰州城市之光":	u"兰州城市之光"
u"余文乐可乐团":	u"余文乐可乐团",
u"S奥森跑团": u"滔来.涛去"

def getMembersByName(pageId, name):
        query = {}
        query["filter"] = {}
        query["filter"]["pageId"] = pageId
        query["limit"] = 1000
        query["offset"] = 0
       
        queryString = json.dumps(query)
        
        ms = govpageService().query(uha.TGovPageMember(), queryString)
        membersInfo = []
        
        for i in ms.result:
            d = objectToDict(i)
            u = userSerializer({"id": d["userId"]})
            if "name" not in u:
                continue
            d["name"] = u["name"]
            if d["name"] == name:
                membersInfo.append({
                    "name": d["name"],
                    "userId": d["userId"],
                    "memberId": d["id"]
                })
        if len(membersInfo) != 1:
            print "error", pageId, membersInfo
        return membersInfo

    
def getPagesByName(name):
    query = {}
    query["filter"] = {}
    query["filter"]["name"] = name
    query["limit"] = 10
    query["offset"] = 0
    queryString = json.dumps(query)
    return govpageService().query(uha.TGovPage(), queryString).result


def getPageExchangeInfo(pageName, memberName):
    pages = getPagesByName(pageName)
    pagesInfo = {}
    if len(pages) != 1:
        print "error:" + pageName + ": dulplicated"
    for p in pages:
        pageInfo = {}
        pageInfo["pageId"] = p.id
        pageInfo["name"] = p.name
        pageInfo["targetUser"] = getMembersByName(p.id, memberName)
        pagesInfo[p.id] = pageInfo

    return pagesInfo


def getPreExchangePages(d=targetPages):
    pages = []
    for k, v in d.items():
        p = getPageExchangeInfo(k, v)
        pages.append(p)
    return pages

    
def exchangeGovPageCreator(pageId, targetUserId):
    govpageService().getById()

tt = [{"100249": {"targetUser": [], "pageId": 100249, "name": "\u72ec\u827a\u65e0\u4e8c"}},
      {"100118": {"targetUser": [{"userId": 100503, "name": "Clown", "memberId": 103047}], "pageId": 100118, "name": "\u5de6\u53f3\u9752\u6625"}},
      {},
      {"100250": {"targetUser": [], "pageId": 100250, "name": "\u66f2\u73ae\u73ae"}},
      {"100117": {"targetUser": [], "pageId": 100117, "name": "\u8bd1\u6797\u51fa\u7248\u793e"}},
      {"100094": {"targetUser": [], "pageId": 100094, "name": "\u7535\u5f71\u516c\u4f1a"}},
      {"100080": {"targetUser": [], "pageId": 100080, "name": "\u679c\u9171\u97f3\u4e50"}},
      {"100113": {"targetUser": [], "pageId": 100113, "name": "\u5929\u6d25BMX\u674e\u6653\u521a"}},
      {"100282": {"targetUser": [], "pageId": 100282, "name": "\u591a\u8309"}, "100253": {"targetUser": [], "pageId": 100253, "name": "\u591a\u8309"}},
      {"100126": {"targetUser": [], "pageId": 100126, "name": "\u8a79\u59c6\u65af\u8d34\u5427"}},
      {"100128": {"targetUser": [], "pageId": 100128, "name": "\u5170\u5dde\u57ce\u5e02\u4e4b\u5149"}},
      {"100116": {"targetUser": [], "pageId": 100116, "name": "\u5c0f\u9504\u5934"}},
      {"100211": {"targetUser": [], "pageId": 100211, "name": "\u6c11\u8c23\u6545\u4e8b"}},
      {"100112": {"targetUser": [], "pageId": 100112, "name": "\u6444\u5f71\u6587\u4e00"}},
      {"100122": {"targetUser": [], "pageId": 100122, "name": "\u5065\u8eab\u6f6e\u4eba"}},
      {"100127": {"targetUser": [], "pageId": 100127, "name": "\u5b81\u6ce2\u706f\u5854\u97f3\u4e50\u73b0\u573a"}},
      {"100287": {"targetUser": [], "pageId": 100287, "name": "\u725b\u4e8c\u676f-\u5317\u4eac\u6500\u5ca9"}},
      {"100125": {"targetUser": [], "pageId": 100125, "name": "\u5e93\u91cc\u4e2d\u6587\u7f51"}},
      {"100129": {"targetUser": [], "pageId": 100129, "name": "\u5468\u6770\u4f26\u6b4c\u8ff7\u7f51"}},
      {"100257": {"targetUser": [], "pageId": 100257, "name": "\u77e5\u66f4\u793e\u533a"}},
      {"100120": {"targetUser": [], "pageId": 100120, "name": "\u7231\u5065\u8eab\u9a91\u8f66\u7684\u6653\u4e39"}},
      {"100246": {"targetUser": [], "pageId": 100246, "name": "\u4e0d\u6b62\u8bfb\u4e66"}},
      {"100265": {"targetUser": [], "pageId": 100265, "name": "\u7bee\u7403\u70ed\u89c6\u9891"}},
      {"100192": {"targetUser": [], "pageId": 100192, "name": "\u56db\u5b63\u5e02\u96c6"}}, {}]


