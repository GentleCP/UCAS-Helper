# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : ui.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 14:00
# @WebSite : https://www.gentlecp.com

import logging
import time
import requests
import os

from core.assess import Assesser
from core.grade import GradeObserver
from core.download import Downloader
from core.exception import BackToMain
from core.wifi import WifiLoginer,WifiError

import settings

WELCOME_MESSAGE = """
*********************************************************************************
**      #   #   ###     #       ###    #  #   ###  #     ###    ###  ####      **
**      #   #  #       # #     #       #  #  #     #     #  #  #     #   #     **
**      #   #  #      #   #    ####    ####  ###   #     ###   ###   ####      **
**      #   #  #     #######      #    #  #  #     #     #     #     #  #      **
**       ###    ### ##     ##  ###     #  #   ###  ##### #      ###  #   #     **
**                            copyright@GentleCP                               **
**                            version: 2.1.1                                   **
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

    def __init__(self, welcome_msg):
        self._logger = logging.getLogger("Init")
        self._welcome_msg = welcome_msg

        self._wifiLoginer = WifiLoginer(accounts_path=settings.ACCOUNTS_PATH)
        self._downloader = Downloader(user_info=settings.USER_INFO,
                                urls=settings.URLS,
                                source_dir=settings.SOURCE_DIR,
                                filter_list=settings.FILTER_LIST)
        self._assesser = Assesser(user_info=settings.USER_INFO,
                            urls=settings.URLS,
                            assess_msgs=settings.ASSESS_MSG)
        self._gradeObserver = GradeObserver(user_info=settings.USER_INFO,
                                      urls=settings.URLS)

    def _show_welcome(self):
        print(self._welcome_msg)


    def _check_update(self, user="GentleCP", repo="UCAS-Helper"):
        api = "https://api.github.com/repos/{user}/{repo}".format(user=user, repo=repo)
        try:
            latest_update_time = requests.get(api).json()["updated_at"]
        except Exception:
            self._logger.error("checking update faild.")
            return False
        try:
            with open("last_update_time.txt", 'r') as f:
                last_update_time = f.readline().strip()
        except FileNotFoundError:
            with open("last_update_time.txt", 'w') as f:
                f.write(latest_update_time)
                return True

        if latest_update_time == last_update_time:
            # already up to date
            return False
        else:
            with open("last_update_time.txt", 'w') as f:
                f.write(latest_update_time)
                return True
    
    
    def _cmd(self):
        while True:
            time.sleep(0.1)
            option = input("输入你的操作：")
            if option == 'q':
                print("欢迎使用，下次再会~")
                exit(200)

            elif not (option.isdigit() and 1<=int(option)<=5) :
                self._logger.warning("非法操作，请重新输入")
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
        if settings.ALLOW_AUTO_UPDATE and self._check_update():
            # do update
            self._logger.info("Available updates detected, start updating...")
            os.system("git stash && git fetch --all && git merge && git stash pop")
            self._logger.info("Update compelte.")
        self._cmd()


def main():

    init = Init(WELCOME_MESSAGE)
    init.run()


if __name__ == "__main__":
    main()
