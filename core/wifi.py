# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : wifi.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 17:06
# @WebSite : https://www.gentlecp.com
import logging
import json
import datetime
import requests
from core.utils import util_login

class WifiError(Exception):
    pass


class WifiLoginer:

    def __init__(self, accounts_path):
        self._logger = logging.getLogger("WifiLoginer")
        self.accounts_path = accounts_path  # 账户信息文件路径
        self.d_accounts = None


    def _set_account_info(self):
        """
        获取可用账户进行登录
        :return: user_info
        """
        try:
            with open(self.accounts_path, 'r') as f:
                try:
                    self.d_accounts = json.loads(f.read())
                except json.decoder.JSONDecodeError:
                    self._logger.error("不是json文件，请按照要求修改内容！")
                    exit(401)
                else:
                    if not self.d_accounts["useful_accounts"]:
                        # 所有账户流量都用完了
                        self._logger.info("没有可用账户!")

        except FileNotFoundError:
            self._logger.error("accounts.json文件不存在，请确认在根目录下创建！")
            exit(404)

    def _check_date(self):
        '''
        检查当前日期，如果是新的一个月，则重置所有账号可用
        :return:
        '''
        current_month = datetime.datetime.now().month
        with open(self.accounts_path, 'r') as f:
            res = json.loads(f.read())
        if res["current_month"] != current_month:
            res["useful_accounts"].extend(res["useless_accounts"])  # 将所有流量耗尽的账户添加到可用账户中
            res["useless_accounts"] = []
            res["current_month"] = current_month
            with open(self.accounts_path, 'w') as f:
                f.write(json.dumps(res))

    def _save_accounts(self,accounts):
        with open(self.accounts_path, 'w') as f:
            f.write(json.dumps(accounts))

    def _change_account(self, msg):
        self._logger.info("正在为您尝试切换可用账户...")
        if msg == '无可用剩余流量!' or "密码不匹配,请输入正确的密码!":
            useless_account = self.d_accounts["useful_accounts"].pop(0)
            self.d_accounts["useless_accounts"].append(useless_account)
        else:
            self.d_accounts["useful_accounts"].pop(0)

    def _check_login(self):
        url = "http://210.77.16.21/eportal/InterFace.do?method=getOnlineUserInfo"
        try:
            res = requests.get(url, timeout=2)
            if res.json()["result"] == 'success':
                # 已经登录
                self._logger.info("您已经登录校园网，无需重复登录！")
                return True
            else:
                self._logger.info("正在为您登录校园网...")
                return False
        except requests.exceptions.ConnectTimeout:
            # 超时说明无法提供ip
            self._logger.error("网络连接超时，请稍后再试！")
            exit(400)

        except requests.exceptions.ReadTimeout:
            self._check_login()

    def _login_wifi(self):
        try:
            stuid = self.d_accounts["useful_accounts"][0]["stuid"]
            password = self.d_accounts["useful_accounts"][0]["pwd"]
        except IndexError:
            self._logger.error("无可用账号！")
            self._save_accounts(self.d_accounts)
            raise WifiError

        login_res = util_login(stuid, password)
        if not login_res:
            self._logger.error("网络连接出错，可能原因：1、未连接上校园网 2、当前网络环境无可分配动态ip")
            raise WifiError

        if login_res.get('result')== 'success':
            self._logger.info("Wifi登录成功，尽情冲浪吧~")
            self._save_accounts(self.d_accounts)
        else:
            self._logger.info("{} 登录失败!原因：{}".format(stuid,login_res.get('msg')))
            self._change_account(login_res.get('msg'))
            self._login_wifi()

    def _get_flow_info(self):
        url = "http://210.77.16.21/eportal/InterFace.do?method=getOnlineUserInfo"
        try:
            res = requests.get(url)
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout):
            self._logger.error("网络连接出现问题，请检查是否已连接上校园网！")
            exit(400)
        else:
            res.encoding = 'u8'
            if res.json().get("message") == "用户信息不完整，请稍后重试":
                return self._get_flow_info()
            else:
                return res.json().get('maxFlow')


    def login(self):
        self._set_account_info()
        if not self._check_login():
            self._login_wifi()
            self._logger.info("剩余流量：{}".format(self._get_flow_info()))

    def logout(self):
        try:
            flow_info = self._get_flow_info()
            if flow_info :
                self._logger.info("剩余流量：{}".format(flow_info))
                requests.get("http://210.77.16.21/eportal/InterFace.do?method=logout")
                self._logger.info("已退出校园网！")
            else:
                self._logger.info("您尚未登录校园网！")

        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout):
            self._logger.error("网络连接出现问题，请检查是否已连接上校园网！")
            raise WifiError

