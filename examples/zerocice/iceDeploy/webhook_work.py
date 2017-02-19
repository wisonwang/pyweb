#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uhaAppServer.core.utils.pingxx import getPingppHelper
from flask import Flask, request, Response
from uhaAppServer.ice_proxy import IceProxyHelp
from uhaAppServer.apps.pay.serializer import PayHelper, payService
from uhaAppServer.core.db.mongo import get_mongo_client, init_mongo
from uhaAppServer.core.utils.simple_serialize import objectToDict
import uha
import json
import logging
import copy

logger = logging.getLogger("uha.webhookwork")

app = Flask(__name__)


def init(configFile="/opt/uhaService/ice-config/service.json"):
    with open(configFile) as f:
        config = json.load(f)
        mongoHost = config.get("mongo-host", "127.0.0.1")
        mongoPort = config.get("mongo-port", 27017)
        mongoMaxPoolSize = config.get("mongo-max-pool-size", 2000)
        init_mongo(mongoHost, mongoPort, mongoMaxPoolSize)


init()

        
def get_db():
    return get_mongo_client("pingxx")


def doHandleChargeSucceeded(event):
    # TODO: xx
    get_db()["chargeSuccess"].save(event)
    orderId = long(event["data"]["object"]["order_no"])
    PayHelper.changeOrderStatus(orderId, "paid")
    o = payService().getById(uha.TOrder(), orderId)
    o.chargeInfo = json.dumps(event["data"]["object"])
    payService().updateById(o)


def doHandleRefundSucceeded(event):
    # TODO: xx
    get_db()["refundSuccess"].save(event)
    orderId = long(event["data"]["object"]["order_no"])
    PayHelper.changeOrderStatus(orderId, "refunded")
    o = payService().getById(uha.TOrder(), orderId)
    o.chargeInfo = json.dumps(event["data"]["object"])
    payService().updateById(o)


_handers = {
    "charge.succeeded": doHandleChargeSucceeded,
    "refund.succeeded": doHandleRefundSucceeded
}


def handlePingxxEvent(event):
    """
    envent.type:
    summary.daily.available	单个应用	上一天 0 点到 23 点 59 分 59 秒的交易金额和交易量统计，在每日 02:00 点左右触发
    summary.weekly.available	单个应用	上周一 0 点至上周日 23 点 59 分 59 秒的交易金额和交易量统计，在每周一 02:00 点左右触发
    summary.monthly.available	单个应用	上月一日 0 点至上月末 23 点 59 分 59 秒的交易金额和交易量统计，在每月一日 02:00 点左右触发
    charge.succeeded	单个应用	支付对象，支付成功时触发
    refund.succeeded	单个应用	退款对象，退款成功时触发
    transfer.succeeded	单个应用	企业支付对象，支付成功时触发
    red_envelope.sent	单个应用	红包对象，红包发送成功时触发
    red_envelope.received
    """
    logger.info(event)
    h = _handers.get(event["type"])
    if h:
        h(event)


@app.route('/pingxx/webhook', methods=['POST'])
def do_pingxx_webhook():
    params = request.get_json()
    logger.info(params)
    
    # event = getPingppHelper().convert_to_pingpp_object(params)
    handlePingxxEvent(params)
    
    return Response(
        str(request.get_json()),
        mimetype='application/json,charset=UTF-8')


@app.route('/test', methods=['POST'])
def do_test():
    params = copy.deepcopy(request.get_json())
    logger.info(params)
    if "_id" in params.keys():
        params.pop("_id")
    return Response(json.dumps(params),
                    mimetype='application/json,charset=UTF-8')


if __name__ == '__main__':
    app.run(debug=True, port=8500, host='0.0.0.0')
    