# -*- coding: utf-8 -*-
"""
-----------------Init-----------------------
            Name: grade.py
            Description:
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Date: 2020-08-31 
-------------Change Logs--------------------


--------------------------------------------
"""
import requests
import logging
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from core.login import Loginer
from handler.logger import LogHandler

class GradeObserver(Loginer):
    """
    课程成绩查看器
    """

    def __init__(self, user_info, urls):
        super().__init__(user_info, urls)
        self._logger = LogHandler('GradeObserver')

    def _show_grade(self):
        try:
            res = self._S.get(self._urls['grade_url']['http'],headers=self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.get(self._urls['grade_url']['https'],headers=self.headers)

        bs4obj = BeautifulSoup(res.text, 'html.parser')
        thead = bs4obj.find('thead')
        pd = PrettyTable()
        pd.field_names = [x.string for x in thead.find_all('th')]

        tbody = bs4obj.find('tbody')
        for tr in tbody.find_all('tr'):
            # tr:每一门课程信息
            pd.add_row([x.string.strip() for x in tr.find_all('td')])
        self._logger.info('成绩查询结果如下')
        print(pd)

    def run(self):
        self.login()
        self._show_grade()


import settings

if __name__ =='__main__':
    gradeObserver = GradeObserver(user_info=settings.USER_INFO,
                                  urls=settings.URLS)
    gradeObserver.run()