# -*- coding: utf-8 -*-
"""
-----------------Init-----------------------
            Name: download.py
            Description: 课程资源下载器
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Date: 2020-08-31 
-------------Change Logs--------------------


--------------------------------------------
"""
import logging
import re
import os
import sys
import requests

from bs4 import BeautifulSoup
from core.login import Loginer
from core.utils import download_file

class Downloader(Loginer):
    def __init__(self, user_info, urls, source_dir,filter_list):
        super().__init__(user_info, urls)
        self._logger = logging.getLogger("Downloader")
        self._source_dir = source_dir
        self._filter_list = filter_list
        self._update_sources = []
        self._l_course_info = []
        self._d_source_info = {}
        self._S = requests.session()
        self._cur_course_info = None
        self._collection_id_pattern = re.compile("value='(?P<collection_id>.*?)';")  # 获取collection id 信息正则
        self._dir_pattern = re.compile("value='/group/[0-9]*/(?P<dir>.*?)';")   # 获取文件夹目录信息正则
        self.__check_dir(self._source_dir)

    def __check_dir(self, dir):
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
            except FileNotFoundError:
                self._logger.error("资源存储路径非法或不正确，请检查settings中SOURCE_DIR配置！")
                exit(404)

    def __update_source_info(self,course_info, bs4obj, dir):
        i = 1
        for e in bs4obj.findAll('a'):
            try:
                if 'course.ucas.ac.cn/access/content/group' in e["href"]:
                    filename = e.find('span', {'class': 'hidden-sm hidden-xs'}).get_text()
                    self._d_source_info[course_info["name"]].append({'id': i,'name': dir+filename, 'url': e["href"]})
                    i += 1
            except (KeyError, AttributeError):
                continue

    def _recur_dir(self,course_info, source_url, bs4obj):
        '''
        递归获取文件夹下文件信息
        :param source_url:
        :param bs4obj:
        :return:
        '''
        l_dir_objs =bs4obj.findAll('a', {'title': '文件夹'})
        if len(l_dir_objs) > 1:
            # 存在其他文件夹，添加当前目录资源信息，接着递归文件夹下内容
            cur_dir = self._dir_pattern.findall(l_dir_objs[0]["onclick"])[0]  # 获取了课程文件夹信息
            self.__update_source_info(course_info, bs4obj, cur_dir)

            csrf_token = bs4obj.find('input', {'name': 'sakai_csrf_token'}).get("value")  # 获取token，用于请求文件夹资源

            for e in bs4obj.findAll('a', {'title': '文件夹'})[1:]:  # 第一个是当前目录忽略
                collection_id = self._collection_id_pattern.findall(e["onclick"])[1]  # 获取了课程文件夹信息
                data = {
                    'source': 0,
                    'collectionId': collection_id,
                    'navRoot': '',
                    'criteria': 'title',
                    'sakai_action': 'doNavigate',
                    'rt_action': '',
                    'selectedItemId': '',
                    'itemHidden': 'false',
                    'itemCanRevise': 'false',
                    'sakai_csrf_token': csrf_token
                }
                res = self._S.post(source_url, data=data)  # 获取文件夹下资源信息
                bs4obj = BeautifulSoup(res.text, 'html.parser')
                self._recur_dir(course_info, source_url, bs4obj)

        else:
            # 没有更深层文件夹了，添加资源信息
            cur_dir = self._dir_pattern.findall(l_dir_objs[0]["onclick"])[0]  # 获取了课程文件夹信息
            self.__update_source_info(course_info, bs4obj, cur_dir)
            return


    def _set_course_info(self):
        if not self._l_course_info:
            # 减少后续多次请求课程信息耗时
            try:
                res = self._S.get(url=self._urls['course_info_url']['http'],timeout=5)
            except requests.Timeout:
                res = self._S.get(url=self._urls['course_info_url']['https'])

            bsobj = BeautifulSoup(res.text, "html.parser")
            refresh_url = bsobj.find("noscript").meta.get("content")[6:]  # 获取新的定向url
            res = self._S.get(refresh_url)
            bsobj = BeautifulSoup(res.text, "html.parser")
            new_course_url = bsobj.find('a', {"title": "我的课程 - 查看或加入站点"}).get("href")  # 获取到新的课程信息url
            res = self._S.get(new_course_url)
            bsobj = BeautifulSoup(res.text, "html.parser")
            course_list = bsobj.findAll('tr')  # 尚未筛选的杂乱信息
            i = 1
            for course in course_list:
                a = course.find('a')
                course_url = a.get("href")
                course_name = a.get_text()
                if "课程名称" not in course_name:
                    self._l_course_info.append({'id': i, 'name': course_name, 'url': course_url})
                    self._d_source_info.update({course_name: []})  # 为该课程开辟一个位置
                    i += 1

    def _set_source_info(self, course_info):
        '''
        给定一门课(name+url)，获取该课的所有课程资源
        :param course:
        :return:
        '''
        if not self._d_source_info[course_info["name"]]:
            # 该门课的资源信息尚未存储到内存
            res = self._S.get(course_info["url"])
            bs4obj = BeautifulSoup(res.text, "html.parser")
            source_url = bs4obj.find('a', {'title': '资源 - 上传、下载课件，发布文档，网址等信息'}).get("href")
            res = self._S.get(source_url)   # 获取课程资源页面
            bs4obj = BeautifulSoup(res.text, "html.parser")

            self._recur_dir(course_info,source_url,bs4obj)


    def __recur_mkdir(self,course_dir, dirs):
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

    def _download_one(self, course_info, source_info):
        '''
        给定一门课，下载该门课指定一个资源
        :return:
        '''
        # 按季度划分课程
        if "秋季" in course_info['name']:
            base_dir = self._source_dir + '/秋季/'
        elif "春季" in course_info['name']:
            base_dir = self._source_dir + '/春季/'
        else:
            base_dir = self._source_dir+ '/夏季/'
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

        course_dir = base_dir + course_info['name']  # 课程目录
        if not os.path.exists(course_dir):
            os.mkdir(course_dir)

        dirs = source_info['name'].split('/')[0:-1]  # 只取目录部分
        if dirs:
            # 存在文件夹，递归检测文件夹
            self.__recur_mkdir(course_dir,dirs)

        file_path = base_dir + course_info["name"] + '/' + source_info['name']  # 文件存储路径
        if not os.path.isfile(file_path):
            # 只下载没有的文件，若存在不下载，节省流量
            self._logger.info("正在下载:{}".format(source_info['name']))
            # content = self._S.get(source_info['url']).content
            # with open(file_path, 'wb') as f:
            #     f.write(content)
            download_file(url=source_info['url'], session=self._S, file_path=file_path)
            self._update_sources.append("[{}:{}]".format(course_info["name"], source_info['name']))  # 记录更新的课程数据

    def _download_course(self, course_info):
        '''
        下载一门课的所有资源
        :param S:
        :param course_info:
        :return:
        '''
        print("\033[1;45m正在同步{}全部资源... \033[0m".format(course_info["name"]))
        for source_info in self._d_source_info[course_info["name"]]:
            self._download_one(course_info, source_info)

    def _download_all(self):
        for course_info in self._l_course_info:
            if course_info['name'] not in self._filter_list:
                self._set_source_info(course_info)
                self._download_course(course_info)
        if self._update_sources:
            self._logger.info("[同步完成] 本次更新资源列表如下：")
            for source in self._update_sources:
                print('\033[1;41m'+source+'\033[0m')

            is_open = input("是否打开资源所在目录(默认n)？(y/n)")
            if is_open == 'y':
                self.__open_dir()
            exit(200)

        else:
            self._logger.info("[同步完成] 本次无更新内容！")
            exit(200)

    def __open_dir(self):
        '''
        当同步完成的时候，打开对应的目录
        :return:
        '''
        if sys.platform.startswith('win'):
            result = os.system('start ' + self._source_dir)
        elif sys.platform.startswith('linux'):
            result = os.system('nautilus ' + self._source_dir)
        else:
            result = os.system('open ' + self._source_dir)
        if result == 0:
            print("已为您打开资源目录，请根据更新资源列表查询对应文件！")
        else:
            print("打开资源目录失败，请手动开启！")

    def _download_course_by_season(self,season):
        for course_info in self._l_course_info:
            if season in course_info['name'] and course_info['name'] not in self._filter_list:
                self._set_source_info(course_info)
                self._download_course(course_info)

        if self._update_sources:
            self._logger.info("[同步完成] 本次更新资源列表如下：")
            for source in self._update_sources:
                print('\033[1;41m' + source + '\033[0m')

            is_open = input("是否打开资源所在目录(默认n)？(y/n)")
            if is_open =='y':
                self.__open_dir()
            exit(200)

        else:
            self._logger.info("[同步完成] 本次无更新内容！")
            exit(200)


    def _show(self, infos):
        if infos:
            for info in infos:
                print("\033[1;45m [{}]:{} \033[0m".format(info['id'], info['name']))
        else:
            print("\033[1;41m尚无信息！\033[0m")

    def __check_option(self, option):
        if option == 'q':
            print("欢迎使用，下次再会~")
            exit(200)

        elif option == 'b' and self._cur_course_info:
            self._cur_course_info = None  # 清空
            return True

        elif option == 'd' and not self._cur_course_info:
            self._download_all()
            return False

        elif option == 's' and not self._cur_course_info:
            self._download_course_by_season('春季')
            return False

        elif option == 'm' and not self._cur_course_info:
            self._download_course_by_season('夏季')
            return False

        elif option == 'f' and not self._cur_course_info:
            self._download_course_by_season('秋季')
            return False

        elif option == 'a' and self._cur_course_info:
            self._download_course(course_info=self._cur_course_info)

        elif option.isdigit() and self._cur_course_info:
            # 课程界面操作
            try:
                source_info = self._d_source_info[self._cur_course_info["name"]][int(option) - 1]
            except IndexError:
                self._logger.warning("不存在该序号课程资源，请重新选择！")
            else:
                self._download_one(self._cur_course_info, source_info)

        elif option.isdigit():
            # 主界面操作
            try:
                self._cur_course_info = self._l_course_info[(int(option) - 1)]
            except IndexError:
                self._logger.warning("不存在该序号课程，请重新选择！")
            else:
                self._set_source_info(self._cur_course_info)
                return True

        else:
            self._logger.warning("非法操作，请重新输入")
            return False

    def _cmd(self):
        while True:
            print("\033[1;45m>课程列表：\033[0m", flush=True)
            self._show(self._l_course_info)
            print("""
***************************************
*       id:显示对应课程的所有资源       *
*       d:一键同步所有资源             *
*       s:同步春季课程资源             *
*       m:同步夏季课程资源             *
*       f:同步秋季课程资源             *
*       q:退出                        *
***************************************
            """)
            option = input("请输入你的操作:")
            if not self.__check_option(option):
                # 不进入下一级界面
                continue
            while True:
                print("\033[1;45m>课程列表>{}:\033[0m".format(self._cur_course_info["name"]))
                self._show(self._d_source_info[self._cur_course_info["name"]])
                print("""
*********************************
*       id:下载对应id资源         *
*       a:下载所有               *
*       b:返回上一级             *
*       q:退出                  *
********************************
                """)
                option = input("请输入你的操作：")
                if self.__check_option(option):
                    # 接收到返回上级界面信息
                    break

    def run(self):
        self.login()
        self._set_course_info()  # 添加所有课程信息到内存中
        self._cmd()  # 进入交互界面


import settings

if __name__ == '__main__':
    downloader = Downloader(user_info=settings.USER_INFO,
                            urls=settings.URLS,
                            source_dir=settings.SOURCE_DIR,
                            filter_list=settings.FILTER_LIST)
    downloader.run()
