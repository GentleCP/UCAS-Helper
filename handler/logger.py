#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-----------------File Info-----------------------
            Name: logger.py
            Description: 日志处理
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Create Date: 2021-01-07 
-----------------End-----------------------------
"""

import os
import logging
import platform
from pathlib import Path

from logging.handlers import TimedRotatingFileHandler

# 日志级别
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

path = Path()

CURRENT_PATH = path.resolve(__file__)
ROOT_PATH = CURRENT_PATH.parent
LOG_PATH = ROOT_PATH.joinpath('log')

if not os.path.exists(LOG_PATH):
    try:
        os.mkdir(LOG_PATH)
    except FileExistsError:
        pass

class LogLevelSetError(Exception):
    pass


class LogHandler(logging.Logger):
    """
    LogHandler
    """

    def __init__(self, name, level=INFO, stream=True, file=True):
        self._name = name
        self._level = level
        logging.Logger.__init__(self, self._name, level=level)
        if stream:
            self.__setStreamHandler__()
        if file:
            if platform.system() != "Windows":
                self.__setFileHandler__()


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, name):
        self._name = name


    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if level in [DEBUG, INFO, WARNING, CRITICAL, ERROR]:
            self._level = level
        else:
            raise LogLevelSetError("Can not set the log level as:{}".format(level))


    def __setFileHandler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """
        file_name = os.path.join(LOG_PATH, '{name}.log'.format(name=self._name))
        # 设置日志回滚, 保存在log目录, 一天保存一个文件, 保留15天
        file_handler = TimedRotatingFileHandler(filename=file_name, when='D', interval=1, backupCount=15)
        file_handler.suffix = '%Y%m%d.log'
        if not level:
            file_handler.setLevel(self._level)
        else:
            file_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s %(filename)s-[line:%(lineno)d] 【%(levelname)s】 %(message)s')

        file_handler.setFormatter(formatter)
        self.file_handler = file_handler
        self.addHandler(file_handler)

    def __setStreamHandler__(self, level=None):
        """
        set stream handler
        :param level:
        :return:
        """
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(filename)s-[line:%(lineno)d] 【%(levelname)s】 %(message)s')
        stream_handler.setFormatter(formatter)
        if not level:
            stream_handler.setLevel(self._level)
        else:
            stream_handler.setLevel(level)
        self.addHandler(stream_handler)


if __name__ == '__main__':
    log = LogHandler('test')
    log.info('this is a test msg')