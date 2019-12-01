# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : utils.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 14:11
# @WebSite : https://www.gentlecp.com
import requests
from urllib.parse import urlparse

def util_login(stuid,password):
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


