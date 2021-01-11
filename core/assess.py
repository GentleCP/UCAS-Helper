# -*- coding: utf-8 -*-
"""
-----------------Init-----------------------
            Name: assess.py
            Description:
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Date: 2020-08-31 
-------------Change Logs--------------------


--------------------------------------------
"""
import re
import time
import requests

from bs4 import BeautifulSoup

from core.login import Loginer
from handler.logger import LogHandler

class Assesser(Loginer):

    def __init__(self,
                 urls=None,
                 user_config_path='../conf/user_config.ini',
                 assess_msgs=[],
                 *args, **kwargs):
        super().__init__(urls, user_config_path, *args, **kwargs)
        self._logger = LogHandler('Assesser')
        self._assess_msgs = assess_msgs

        self._id_pattern = re.compile('/evaluate/.*?/(?P<id>.*?)$')
        self._course_assess_url = None  # 动态获取课程评估地址


    def _get_course_ids(self):
        # 获取课程评估url
        try:
            res = self._S.get(url=self._urls['view_url']['http'], headers=self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.get(url=self._urls['view_url']['https'], headers=self.headers)
        bs4obj = BeautifulSoup(res.text,'html.parser')
        href = bs4obj.find('a',string=re.compile('.*学期$')).get('href')
        self._course_assess_url = self._urls['base_url']['http'] + href
        # 获取课程id
        try:
            res = self._S.get(self._course_assess_url, headers=self.headers, timeout=5)
        except requests.Timeout:
            self._course_assess_url = self._urls['base_url']['https'] + href
            res = self._S.get(self._course_assess_url, headers=self.headers)

        bs4obj = BeautifulSoup(res.text, 'html.parser')
        urls = [url.get('href') for url in bs4obj.find_all('a', {'class': 'btn'})]
        course_ids = []
        for url in urls:
            course_ids.append(self._id_pattern.search(url).groupdict()['id'])
        return course_ids


    def __assess_course(self,course_id):
        try:
            res = self._S.get(self._urls['base_evaluateCourse_url']['http'] + course_id, headers=self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.get(self._urls['base_evaluateCourse_url']['https'] + course_id, headers=self.headers)

        s = res.text.split('?s=')[-1].split('"')[0]
        bs4obj = BeautifulSoup(res.text, 'html.parser')
        radios = bs4obj.find_all('input', attrs={'type': 'radio'})
        value = radios[0]['value']
        data = {}
        for radio in radios:
            data[radio['name']] = value
        textareas = bs4obj.find_all('textarea')
        for textarea, asses_msg in zip(textareas,self._assess_msgs[0:-2]):
            # 填写主观评价内容
            item_id = textarea.get('id')
            data[item_id] = asses_msg
        subjectiveRadio = bs4obj.find('input', {'class':'required radio'}).get('id')
        subjectiveCheckbox = bs4obj.find('input',{'class','required checkbox'}).get('id')
        data['subjectiveRadio']= subjectiveRadio   # 教室大小合适
        data['subjectiveCheckbox']= subjectiveCheckbox  # 自己需求和兴趣

        try:
            post_url = self._urls['base_saveCourseEval_url']['http'] + course_id + '?s=' + s
            res = self._S.post(post_url, data=data,headers=self.headers,timeout=5)
        except requests.Timeout:
            post_url = self._urls['base_saveCourseEval_url']['https'] + course_id + '?s=' + s
            res = self._S.post(post_url, data=data, headers=self.headers)
        tmp = BeautifulSoup(res.text, 'html.parser')
        try:
            flag = tmp.find('label', attrs={'id': 'loginSuccess'})
            if flag.string == '保存成功':
                print('\033[1;45m{}评估结果：[success] \033[0m'.format(course_id))
            else:
                print('\033[1;45m{}评估结果：[fail]，请手动重新评估该课 \033[0m'.format(course_id))

        except AttributeError:
            print('\033[1;45m{}评估结果：[fail]，尝试重新评估 \033[0m'.format(course_id))
            self.__assess_course(course_id)


    def _assess_courses(self, course_ids):
        self._logger.info('开始评估课程')
        time.sleep(2)
        for course_id in course_ids:
            self.__assess_course(course_id)
        self._logger.info('课程评估完毕')


    def _get_teacher_ids(self):
        # 通过课程评估url得到教师评估url
        teacher_assess_url = self._course_assess_url.replace('course','teacher')
        res = self._S.get(teacher_assess_url, headers=self.headers)
        bs4obj = BeautifulSoup(res.text, 'html.parser')
        urls = [url.get('href') for url in bs4obj.find_all('a', {'class': 'btn'})]
        teacher_ids = []
        for url in urls:
            teacher_ids.append(self._id_pattern.search(url).groupdict()['id'])
        return teacher_ids

    def __assess_teacher(self, teacher_id):
        try:
            res = self._S.get(self._urls['base_evaluateTeacher_url']['http'] + teacher_id, headers=self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.get(self._urls['base_evaluateTeacher_url']['https'] + teacher_id, headers=self.headers)

        bs4obj = BeautifulSoup(res.text,'lxml')
        radios = bs4obj.find_all('input', attrs={'type': 'radio'})
        value = radios[0]['value']  # 默认全5星好评
        data = {}
        for radio in radios:
            data[radio['name']] = value
        textareas = bs4obj.find_all('textarea')
        for textarea, asses_msg in zip(textareas, self._assess_msgs[-2:]):
            # 填写主观评价内容
            item_id = textarea.get('id')
            data[item_id] = asses_msg
        data['subjectiveCheckbox'] = ''
        data['subjectiveRadio'] = ''
        post_action = bs4obj.find('form', {'id': 'regfrm'})
        try:
            post_url = self._urls['base_url']['http'] + post_action.get('action')
        except requests.Timeout:
            post_url = self._urls['base_url']['https'] + post_action.get('action')
        try:
            res = self._S.post(post_url, data=data, headers=self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.post(post_url, data=data, headers=self.headers)

        tmp = BeautifulSoup(res.text, 'html.parser')
        try:
            flag = tmp.find('label', attrs={'id': 'loginSuccess'})
            if flag.string == '保存成功':
                print('\033[1;45m{}评估结果：[success] \033[0m'.format(teacher_id))
                return
            else:
                print('\033[1;45m{}评估结果：[fail]，请手动评估该教师 \033[0m'.format(teacher_id))

        except AttributeError:
            print('\033[1;45m{}评估结果：[fail]，尝试重新评估 \033[0m'.format(teacher_id))
            self.__assess_teacher(teacher_id)


    def _assess_teachers(self, teacher_ids):
        self._logger.info('开始评估教师')
        for teacher_id in teacher_ids:
            self.__assess_teacher(teacher_id)
        self._logger.info('教师评估完毕')


    def run(self):
        self.login()
        course_ids = self._get_course_ids()
        self._assess_courses(course_ids)
        teacher_ids = self._get_teacher_ids()
        self._assess_teachers(teacher_ids)


import settings
if __name__ =='__main__':
    assesser = Assesser(
                        urls=settings.URLS,
                        assess_msgs=settings.ASSESS_MSG)
    assesser.run()