# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : ui.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 14:00
# @WebSite : https://www.gentlecp.com

import logging
import time

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
**                            version: 2.0.5                                   **
**                github: https://github.com/GentleCP/UCASHelper               **
**                            1:course sources download                        **
**                            2:wifi login                                     **
**                            3:wifi logout                                    **
**                            4:course assess                                  **
**                            5:query grades                                   **
**                            q:exit                                           **
*********************************************************************************
"""


class Init:
    """
    用于检查一切配置信息是否合理正确
    """

    def __init__(self,
                 welcome_msg,
                 wifiLoginer=None,
                 downloader=None,
                 assesser= None,
                 gradeObserver = None,
                 ):
        self._logger = logging.getLogger("Init")
        self._welcome_msg = welcome_msg
        self._wifi_loginer = wifiLoginer
        self._downloader = downloader
        self._assesser = assesser
        self._grade_observer = gradeObserver

    def _show_welcome(self):
        print(self._welcome_msg)

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
                        self._wifi_loginer.login()
                    except WifiError:
                        pass

                elif option == 3:
                    try:
                        self._wifi_loginer.logout()
                    except WifiError:
                        pass

                elif option == 4:
                    self._assesser.run()

                elif option == 5:
                    self._grade_observer.run()

    def run(self):
        self._show_welcome()
        self._cmd()


def main():
    wifiLoginer = WifiLoginer(accounts_path=settings.ACCOUNTS_PATH)
    downloader = Downloader(user_info=settings.USER_INFO,
                            urls=settings.URLS,
                            source_dir=settings.SOURCE_DIR,
                            filter_list = settings.FILTER_LIST)
    assesser = Assesser(user_info=settings.USER_INFO,
                        urls=settings.URLS,
                        assess_msgs=settings.ASSESS_MSG)
    gradeObserver = GradeObserver(user_info=settings.USER_INFO,
                                  urls=settings.URLS)
    init = Init(WELCOME_MESSAGE, wifiLoginer, downloader,assesser, gradeObserver)
    init.run()


if __name__ == "__main__":
    main()
