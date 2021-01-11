#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-----------------File Info-----------------------
            Name: functions.py
            Description: 工具函数
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Create Date: 2020-12-29 
-----------------End-----------------------------
"""

import requests
import os
import sys
import logging
from tqdm import tqdm
from configparser import ConfigParser

from handler.exception import ConfigReadError


def download_file(url, session=None, file_path='未命名文件', overwrite = False):
    '''
    根据指定url下载文件
    :param url:
    :param session: 传入的会话参数，有的需要登录才能下载
    :param file_path: 文件存储路径，默认为当前目录下，存储文件为未命名文件
    :param overwrite: 是否覆盖同名文件，默认否
    :return: 正确下载返回True，否则False
    '''
    if session:
        res = session.get(url, stream = True)
    else:
        res = requests.get(url,stream=True)
    file_size = int(res.headers['content-length'])
    chunk_size = 1024
    if res.status_code == 200:
        if not overwrite and os.path.exists(file_path):
            return True
        else:
            progress_bar = tqdm(
                total=file_size,initial=0,unit='B',unit_scale=True,
            )
            with open(file_path,'wb') as f:
                for data in res.iter_content(chunk_size=chunk_size):
                    if data:
                        f.write(data)
                        progress_bar.update(chunk_size)
            progress_bar.close()
    else:
        logging.error('download fail.')
        return False


def check_dir(dir):
    if not os.path.exists(dir):
        try:
            os.mkdir(dir)
            return False
        except FileNotFoundError:
            return True


def recur_mkdir(course_dir, dirs):
    '''
    递归检查目录是否存在，若不存在则创建
    :param dirs:
    :return:
    '''
    rec_dir = course_dir  # 递归查询的目录
    while dirs:
        rec_dir = rec_dir + '/' + dirs[0]
        if not os.path.exists(rec_dir):
            os.mkdir(rec_dir)
        del dirs[0]


def open_dir(dir):
    '''
    打开指定目录窗口
    :return:
    '''
    if sys.platform.startswith('win'):
        result = os.system('start ' + dir)
    elif sys.platform.startswith('linux'):
        result = os.system('nautilus ' + dir)
    else:
        result = os.system('open ' + dir)
    return result


def get_cfg(config_path):
    '''
    基于给定的配置路径生成ConfigParser
    :param config_path:
    :return: cfg
    '''
    cfg = ConfigParser()
    cfg.read(config_path, encoding='utf-8')
    return cfg
