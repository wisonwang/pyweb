# -*- coding: utf-8 -*-
from uhaAppServer.core.singleton import singleton


@singleton
class ErrorCode:
    def __init__(self, *args, **kwargs):
        self.ERROR_OK = 200
        self.ERROR_USER_LONGIN_FAIL = 10001
        self.ERROR_USER_PERMISSION_DENY = 10002
        self.ERROR_USER_OPERATION_FAILED = 10003
        self.ERROR_USER_NOT_LONGIN = 10004
        self.ERROR_USER_SMS_CODE_ERROR = 10005
        self.ERROR_SYS_ERROR = 20001


ERROR_CODE_MAPPING = {}
d = ErrorCode()
for k, v in d.__dict__.items():
    ERROR_CODE_MAPPING[v] = k


def getErrorCodeTips(code):
    return ERROR_CODE_MAPPING.get(code)


class UserException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


def getUserException(verb):
    return UserException(
        ErrorCode().ERROR_USER_OPERATION_FAILED, verb)


def getSMSCodeException():
    return UserException(
        ErrorCode().ERROR_USER_SMS_CODE_ERROR, "sms verify code error")
