# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : source.py
# @Item    : PyCharm
# @Time    : 2019-11-18 15:51
# @WebSite : https://www.gentlecp.com

import os
import sys
import logging
import re
import requests

from bs4 import BeautifulSoup

sys.setrecursionlimit(100000)


class BackToMain(Exception):
    pass


class Loginer:
    def __init__(self, user_info, urls):
        self._logger = logging.getLogger("Loginer")
        self._S = requests.session()
        self._user_info = user_info
        self._urls = urls

    def _login(self):
        headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'http://onestop.ucas.ac.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://onestop.ucas.ac.cn/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        try:
            res = self._S.post(url=self._urls["login_url"], data=self._user_info, headers=headers, timeout=5)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
            self._logger.error("网络连接失败，请确认你的网络环境后重试！")
            exit(400)
        else:
            json_res = res.json()
            if json_res["f"]:
                self._S.get(res.json()["msg"])
                self._logger.info("登录成功！")

            else:
                self._logger.error("登录失败，请检查settings下的USER_INFO是否正确！")
                exit(401)


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
            res = self._S.get(url=self._urls['course_info_url'])
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
            content = self._S.get(source_info['url']).content
            with open(file_path, 'wb') as f:
                f.write(content)
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
        else:
            self._logger.info("[同步完成] 本次无更新内容！")

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
            if is_open:
                self.__open_dir()
            exit(200)

        else:
            self._logger.info("[同步完成] 本次无更新内容！")

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
        self._login()
        self._set_course_info()  # 添加所有课程信息到内存中
        self._cmd()  # 进入交互界面


class Assesser(Loginer):

    def __init__(self, user_info, urls,assess_msg):
        super().__init__(user_info, urls)
        self._logger = logging.getLogger("Assesser")
        self._assess_msg = assess_msg
        self.headers =  {
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
        self._id_pattern = re.compile('/evaluate/.*?/(?P<id>.*?)$')

    def _get_course_ids(self):
        res = self._S.get(url=self._urls['course_select_url'])
        course_select_url = re.search(r"window.location.href='(?P<course_select_url>.*?)'", res.text).groupdict().get(
            "course_select_url")
        self._S.get(course_select_url)

        res = self._S.get(self._urls['course_assess_url'])
        bs4obj = BeautifulSoup(res.text, 'html.parser')
        urls = [url.get('href') for url in bs4obj.find_all('a', {'class': 'btn'})]
        course_ids = []
        for url in urls:
            course_ids.append(self._id_pattern.search(url).groupdict()['id'])
        return course_ids

    def __assess_course(self,course_id):
        res = self._S.get('http://jwxk.ucas.ac.cn/evaluate/evaluateCourse/' + course_id )
        s = res.text.split('?s=')[-1].split('"')[0]
        soup = BeautifulSoup(res.text, 'html.parser')
        radios = soup.find_all('input', attrs={'type': 'radio'})
        value = radios[0]['value']
        data = {}
        for radio in radios:
            data[radio['name']] = value
        data['item_14']= self._assess_msg['item_14']  # 这门课我最喜欢什么
        data['item_15']= self._assess_msg['item_15']  # 我认为本课程应从哪些方面需要进一步改进和提高？
        data['item_16']= self._assess_msg['item_16']  # 我平均每周在这门课程上花费多少小时？
        data['item_17']= self._assess_msg['item_17']  # 在参与这门课之前，我对这个学科领域兴趣如何
        data['item_18']= self._assess_msg['item_18']  # 我对该课程的课堂参与度（包括出勤、回答问题等）
        data['item_25']=''
        data['radio_19']=''
        data['subjectiveRadio']= '20'   # 教室大小合适
        data['subjectiveCheckbox']= '27'  # 自己需求和兴趣

        res = self._S.post('http://jwxk.ucas.ac.cn/evaluate/saveCourseEval/'+course_id+'?s='+s, data=data,headers=self.headers)

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
        for course_id in course_ids:
            self.__assess_course(course_id)
        self._logger.info('课程评估完毕')


    def _get_teacher_ids(self):
        res = self._S.get(self._urls['teacher_assess_url'])
        bs4obj = BeautifulSoup(res.text, 'html.parser')
        urls = [url.get('href') for url in bs4obj.find_all('a', {'class': 'btn'})]
        teacher_ids = []
        for url in urls:
            teacher_ids.append(self._id_pattern.search(url).groupdict()['id'])
        return teacher_ids

    def __assess_teacher(self, teacher_id):
        res = self._S.get('http://jwxk.ucas.ac.cn/evaluate/evaluateTeacher/' + teacher_id)
        bs4obj = BeautifulSoup(res.text,'html.parser')
        submit_url = 'http://jwxk.ucas.ac.cn' + bs4obj.find('form',{'id':'regfrm'}).get('action')
        radios = bs4obj.find_all('input', attrs={'type': 'radio'})
        value = radios[0]['value']  # 默认全5星好评
        data = {}
        for radio in radios:
            data[radio['name']] = value
        data['item_43'] = self._assess_msg['item_43']  # 这位老师的教学，你最喜欢什么？
        data['item_44'] = self._assess_msg['item_44'] # 您对老师有哪些意见和建议？
        data['subjectiveRadio'] = ''
        data['subjectiveCheckbox'] = ''
        res = self._S.post(submit_url,data=data,headers = self.headers)
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
        self._login()
        course_ids = self._get_course_ids()
        self._assess_courses(course_ids)
        teacher_ids = self._get_teacher_ids()
        self._assess_teachers(teacher_ids)

