# -*- coding: utf-8 -*-
"""
-----------------Init-----------------------
            Name: login.py
            Description:
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Date: 2020-08-31 
-------------Change Logs--------------------


--------------------------------------------
"""
import re
import requests
import settings
import json
import warnings

import configparser
from handler.logger import LogHandler
from handler.exception import ExitStatus
from util.functions import get_cfg

warnings.filterwarnings('ignore')


class Loginer(object):
    """
    登录课程网站
    """
    def __init__(self,
                 urls=None,
                 user_config_path='../conf/user_config.ini',
                 *args, **kwargs):
        '''
        :param urls:
        :param user_config_path:
        :param args:
        :param kwargs: 目前仍支持从settings中读取设备,后续考虑移除
        '''
        self._logger = LogHandler("Loginer")
        self._S = requests.session()
        self._user_config_path = user_config_path
        self._user_info_from_settings = kwargs.get('user_info')
        self._cfg = get_cfg(self._user_config_path)
        self._urls = urls

        self.headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Google Chrome";v="87", "\\"Not;A\\\\Brand";v="99", "Chromium";v="87"',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://onestop.ucas.ac.cn',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://onestop.ucas.ac.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }


    def _set_user_info(self):
        '''
        set user info from conf/user_config.ini or from settings.py
        :return: None
        '''

        from_settings_warning_msg = ('Note: you are using the user info from settings.py which may remove in the future, '
                                 'I suggest you to save the user info in conf/user_config.ini')
        try:
            username = self._cfg.get('user_info', 'username')
            password = self._cfg.get('user_info', 'password')
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            self._logger.warning('Can not read user info from {}, try to get it from settings.py'.format(self._user_config_path))
            self._logger.warning(from_settings_warning_msg)
            self._user_info = self._user_info_from_settings
        else:
            if not username or not password:
                # 用户名或密码信息为空
                self._logger.warning(from_settings_warning_msg)
                self._user_info = self._user_info_from_settings
            else:
                self._user_info = {
                    'username': username,
                    'password': password,
                    'remember': 'undefined'
                }


    def __keep_session(self):
        try:
            res = self._S.get(url=self._urls['course_select_url']['http'], headers = self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.get(url=self._urls['course_select_url']['https'], headers = self.headers)
        course_select_url = re.search(r"window.location.href='(?P<course_select_url>.*?)'", res.text).groupdict().get(
            "course_select_url")
        self._S.get(course_select_url,headers=self.headers)


    def login(self):
        self._set_user_info()
        self._S.get(url=self._urls['home_url']['https'], headers=self.headers, verify=False)  # 获取identity
        res = None
        try:
            res = self._S.post(url=self._urls["login_url"]['https'], data=self._user_info, headers=self.headers, timeout=10)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
            self._logger.error("网络连接失败，请确认你的网络环境后重试！")
            exit(ExitStatus.NETWORK_ERROR)
        if res.status_code != 200:
            self._logger.error('sep登录失败，未知错误，请到github提交issue，等待作者修复.')
            exit(ExitStatus.UNKNOW_ERROR)
        else:
            json_res = res.json()
            if json_res["f"]:
                self._S.get(res.json()["msg"], headers=self.headers)
                self._logger.info("sep登录成功！")
                self.__keep_session()
            else:
                self._logger.error("sep登录失败，请检查你的用户名和密码设置是否正确！")
                exit(ExitStatus.CONFIG_ERROR)


if __name__ == '__main__':
    loginer = Loginer(user_info=settings.USER_INFO,
                      urls=settings.URLS,
                      user_config_path='../conf/user_config.ini')
    loginer.login()