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
import warnings
warnings.filterwarnings('ignore')

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

    def __keep_session(self):
        try:
            res = self._S.get(url=self._urls['course_select_url']['http'], headers = self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.get(url=self._urls['course_select_url']['https'], headers = self.headers)
        course_select_url = re.search(r"window.location.href='(?P<course_select_url>.*?)'", res.text).groupdict().get(
            "course_select_url")
        self._S.get(course_select_url,headers=self.headers)

    def login(self):
        self._S.get(url="https://onestop.ucas.ac.cn/", headers=self.headers, verify=False)  # 获取identity
        res = None
        try:
            res = self._S.post(url=self._urls["login_url"]['https'], data=self._user_info, headers=self.headers, timeout=10)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
            self._logger.error("网络连接失败，请确认你的网络环境后重试！")
            exit(400)

        try:
            json_res = res.json()
        except json.decoder.JSONDecodeError:
            self._logger.info("站点https证书失效，更换到http请求")
            res = self._S.post(url=self._urls["login_url"]['http'], data=self._user_info, headers=self.headers,timeout=5)
            json_res = res.json()

        if json_res["f"]:
            self._S.get(res.json()["msg"], headers=self.headers)
            self._logger.info("sep登录成功！")
            self.__keep_session()


        else:
            self._logger.error("sep登录失败，请检查settings下的USER_INFO是否正确！")
            exit(401)


if __name__ == '__main__':
    loginer = Loginer(user_info=settings.USER_INFO,
                      urls=settings.URLS)
    loginer.login()