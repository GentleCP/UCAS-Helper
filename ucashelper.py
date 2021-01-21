# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : ucashelper.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 13:58
# @WebSite : https://www.gentlecp.com


import click
import sys
import os

from handler import ui
from core.wifi import AccHacker
from core.assess import Assesser
from core.grade import GradeObserver
from core.download import Downloader
from core.wifi import WifiLoginer
from handler.configer import UCASHelperConfigApp

import settings

ROOT_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_PATH)


@click.group()
def start():
    """UCASHelper is a useful tool for UCASer, following are the arguments that you could choose"""

@click.command(name='config',help='Set your user info and download path')
def config():
    UCASHelperConfigApp().run()


@click.command(name='ui',help='Get UI interface of UCASHelper')
def UI():
    ui.main(record_path=settings.RECORD_PATH)


@click.command(name='down',help='Download resources from sep website')
def download_source():
    downloader = Downloader(
        user_config_path=settings.USER_CONFIG_PATH,
        user_info=settings.USER_INFO,  # 未来删除
        urls=settings.URLS,
        resource_path=settings.SOURCE_DIR,  # 未来删除
        filter_list=settings.FILTER_LIST)
    downloader.run()


@click.command(name='assess',help='Auto assess courses and teachers')
def auto_assess():
    assesser = Assesser(
        user_config_path=settings.USER_CONFIG_PATH,
        user_info=settings.USER_INFO,  # 未来删除
        urls=settings.URLS,
        assess_msgs=settings.ASSESS_MSG)
    assesser.run()


@click.command(name='grade',help='Query your grades')
def query_grades():
    gradeObserver = GradeObserver(
        user_config_path=settings.USER_CONFIG_PATH,
        user_info=settings.USER_INFO,  # 未来删除
        urls=settings.URLS)
    gradeObserver.run()


@click.command(name='hack',help='Hack wifi accounts')
def hack_accounts():
    hacker = AccHacker(data_path='data/data.txt', password_path='data/password.txt')
    hacker.run()

@click.command(name='login',help='Login campus network')
def login_wifi():
    wifiLoginer = WifiLoginer(accounts_path=settings.ACCOUNTS_PATH)
    wifiLoginer.login()


@click.command(name='logout',help='Logout campus network')
def logout_wifi():
    wifiLoginer = WifiLoginer(accounts_path=settings.ACCOUNTS_PATH)
    wifiLoginer.logout()


if __name__ == '__main__':
    commands = [UI,auto_assess,download_source,query_grades,hack_accounts,login_wifi,logout_wifi, config]
    for command in commands:
        start.add_command(command)
    start()
