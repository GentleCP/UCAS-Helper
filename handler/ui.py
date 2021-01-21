# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : ui.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 14:00
# @WebSite : https://www.gentlecp.com

import time
import requests
import os
import configparser
import json

from core.assess import Assesser
from core.grade import GradeObserver
from core.download import Downloader
from handler.exception import BackToMain, ExitStatus
from core.wifi import WifiLoginer,WifiError
from handler.logger import LogHandler
from util.functions import get_cfg


import settings


WELCOME_MESSAGE = """
*********************************************************************************
**      #   #   ###     #       ###    #  #   ###  #     ###    ###  ####      **
**      #   #  #       # #     #       #  #  #     #     #  #  #     #   #     **
**      #   #  #      #   #    ####    ####  ###   #     ###   ###   ####      **
**      #   #  #     #######      #    #  #  #     #     #     #     #  #      **
**       ###    ### ##     ##  ###     #  #   ###  ##### #      ###  #   #     **
**                            copyright@GentleCP                               **
**                            version:{tag}                                   **
**                github: https://github.com/GentleCP/UCASHelper               **
**                            1:course sources download                        **
**                            2:wifi login                                     **
**                            3:wifi logout                                    **
**                            4:course assess                                  **
**                            5:query grades                                   **
**                            q:exit                                           **
*********************************************************************************
"""


class Init(object):
    """
    用于检查一切配置信息是否合理正确
    """

    def __init__(self,
                 welcome_msg,
                 record_path='../conf/record.ini',
                 *args,**kwargs):
        self._logger = LogHandler("Init")
        self._welcome_msg = welcome_msg

        self._record_path = record_path
        self._cfg = get_cfg(config_path=self._record_path)

        self._name_of_update_section = 'update_info'
        self._name_of_update_time = 'last_update_time'   # 记录上次更新的时间
        self._name_of_tag = 'tag'  # 当前版本号

        # update api info
        self.__update_info_api = "https://api.github.com/repos/GentleCP/UCAS-Helper"
        self.__latest_tag_api = "https://api.github.com/repos/GentleCP/UCAS-Helper/tags"

        self._wifiLoginer = WifiLoginer(accounts_path=settings.ACCOUNTS_PATH)
        self._downloader = Downloader(
                                user_info=settings.USER_INFO,  # 未来删除
                                urls=settings.URLS,
                                user_config_path=settings.USER_CONFIG_PATH,
                                resource_path=settings.SOURCE_DIR,  # 未来删除
                                filter_list=settings.FILTER_LIST)

        self._assesser = Assesser(
                                user_info=settings.USER_INFO,  # 未来删除
                                user_config_path=settings.USER_CONFIG_PATH,
                                urls=settings.URLS,
                                assess_msgs=settings.ASSESS_MSG)
        self._gradeObserver = GradeObserver(
                                user_config_path=settings.USER_CONFIG_PATH,
                                user_info=settings.USER_INFO,  # 未来删除
                                urls=settings.URLS)

    def __get_tag(self):
        '''
        从配置文件或在线获取当前版本号
        :return: tag, e.g. v2.3.1
        '''
        if not self._cfg.has_section(self._name_of_update_section):
            self._cfg.add_section(self._name_of_update_section)
        try:
            local_tag = self._cfg.get(self._name_of_update_section, self._name_of_tag)
        except configparser.NoOptionError:
            self._logger.info('getting latest tag')
            return json.loads(requests.get(self.__latest_tag_api).text)[0].get('name')
        else:
            if not local_tag:
                self._logger.info('getting latest tag')
                return json.loads(requests.get(self.__latest_tag_api).text)[0].get('name')
            else:
                return local_tag



    def _show_welcome(self):
        '''
        :return:
        '''
        tag = self.__get_tag()
        print(self._welcome_msg.format(tag=tag))


    def __check_update(self):
        '''
        check the latest code from github repo api, if detect the new version, update the demo
        :return: {}, if need update, return True and latest_update_time, else return False
        '''
        self._logger.info("Checking update...")

        try:
            latest_update_time = requests.get(self.__update_info_api).json()["updated_at"]
            latest_tag = json.loads(requests.get(self.__latest_tag_api).text)[0].get('name')
        except Exception:
                self._logger.error("checking update faild.")
                return {
                    'need_update':False
                }
        try:
            last_update_time = self._cfg.get(self._name_of_update_section, self._name_of_update_time)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            self._logger.info("Available updates detected, start updating...")
            return {
                'need_update':True,
                'latest_update_time':latest_update_time,
                'latest_tag': latest_tag
            }
        else:
            if latest_update_time == last_update_time:
                # already up to date
                self._logger.info("Already up to date.")
                return {
                    'need_update':False
                }
            else:
                self._logger.info("Available updates detected, start updating...")
                return {
                    'need_update': True,
                    'latest_update_time':latest_update_time,
                    'latest_tag': latest_tag
                }


    def _do_update(self):
        if not settings.ALLOW_AUTO_UPDATE:
            # not allow update
            return
        check_update_res = self.__check_update()
        if check_update_res['need_update']:
            # need to update
            try:
                os.system("git stash && git fetch --all && git merge && git stash pop")
            except KeyboardInterrupt:
                # update interrupt, nothing to do.
                self._logger.error("Update Interrupt by user.")
            else:
                # update complete, update the local update time.
                if not self._cfg.has_section(self._name_of_update_section):
                    self._cfg.add_section(self._name_of_update_section)

                # update latest_update_time
                self._cfg.set(self._name_of_update_section,
                              self._name_of_update_time,
                              check_update_res['latest_update_time'])
                # update latest_tag
                self._cfg.set(self._name_of_update_section,
                              self._name_of_tag,
                              check_update_res['latest_tag'])
                self._cfg.write(open(self._record_path, 'w'))
                self._logger.info("Update compelte.")


    def _cmd(self):
        while True:
            time.sleep(0.1)
            option = input("输入你的操作：")
            if option == 'q':
                print("欢迎使用，下次再会~")
                exit(ExitStatus.OK)

            elif not (option.isdigit() and 1<=int(option)<=5) :
                self._logger.error("非法操作，请重新输入")
            else:
                option = int(option)
                if option == 1:
                    try:
                        self._downloader.run()
                    except BackToMain:
                        pass

                elif option == 2:
                    try:
                        self._wifiLoginer.login()
                    except WifiError:
                        pass

                elif option == 3:
                    try:
                        self._wifiLoginer.logout()
                    except WifiError:
                        pass

                elif option == 4:
                    self._assesser.run()

                elif option == 5:
                    self._gradeObserver.run()


    def run(self):
        self._show_welcome()
        self._do_update()
        self._cmd()


def main(*args, **kwargs):
    init = Init(welcome_msg=WELCOME_MESSAGE, *args, **kwargs)
    init.run()


if __name__ == "__main__":
    main()
