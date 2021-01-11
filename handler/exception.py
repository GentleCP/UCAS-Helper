# -*- coding: utf-8 -*-
"""
-----------------Init-----------------------
            Name: exception.py
            Description:
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Date: 2020-08-31 
-------------Change Logs--------------------


--------------------------------------------
"""
from enum import IntEnum

class ExitStatus(IntEnum):

    OK = 200
    CONFIG_ERROR = 401
    NETWORK_ERROR = 404
    UNKNOW_ERROR = 500

class ConfigReadError(Exception):
    pass


class BackToMain(Exception):
    pass

class WifiError(Exception):
    pass

class HttpError(Exception):
    pass
