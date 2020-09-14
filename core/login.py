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
import logging
import re
import requests
import settings
import json

from core.exception import HttpError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s:[%(message)s]')

class Loginer(object):
    def __init__(self, user_info, urls):
        self._logger = logging.getLogger("Loginer")
        self._S = requests.session()
        self._user_info = user_info
        self._urls = urls
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'http://jwxk.ucas.ac.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://jwxk.ucas.ac.cn/evaluate/evaluateCourse/165683',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def __keep_session(self):
        try:
            res = self._S.get(url=self._urls['course_select_url']['http'],timeout=5)
        except requests.Timeout:
            res = self._S.get(url=self._urls['course_select_url']['https'])
        course_select_url = re.search(r"window.location.href='(?P<course_select_url>.*?)'", res.text).groupdict().get(
            "course_select_url")
        self._S.get(course_select_url,headers=self.headers)

    def login(self):
        try:
            res = self._S.post(url=self._urls["login_url"]['http'], data=self._user_info, headers=self.headers, timeout=10)

        except (requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
            self._logger.error("网络连接失败，请确认你的网络环境后重试！")
            exit(400)

        else:
            if res.status_code == 200:
                json_res = res.json()
            else:
                res = self._S.post(url=self._urls["login_url"]['https'], data=self._user_info, headers=self.headers, timeout=5)
                json_res = res.json()

            if json_res["f"]:
                self._S.get(res.json()["msg"])
                self._logger.info("sep登录成功！")
                self.__keep_session()


            else:
                self._logger.error("sep登录失败，请检查settings下的USER_INFO是否正确！")
                exit(401)


if __name__ == '__main__':
    loginer = Loginer(user_info=settings.USER_INFO,
                      urls=settings.URLS)
    loginer.login()