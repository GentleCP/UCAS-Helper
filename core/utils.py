# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : utils.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 14:11
# @WebSite : https://www.gentlecp.com
import requests
import os
import logging
from tqdm import tqdm
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


def download_file(url, session=None, file_path='未命名文件', overwrite = False):
    '''
    根据指定url下载文件
    :param url:
    :param session: 传入的会话参数，有的需要登录才能下载
    :param file_path: 文件存储路径，默认为当前目录下，存储文件为未命名文件
    :param overwrite: 是否覆盖同名文件，默认否
    :return: 正确下载返回True，否则False
    '''
    if session:
        res = session.get(url, stream = True)
    else:
        res = requests.get(url,stream=True)
    file_size = int(res.headers['content-length'])
    chunk_size = 1024
    if res.status_code == 200:
        if not overwrite and os.path.exists(file_path):
            return True
        else:
            progress_bar = tqdm(
                total=file_size,initial=0,unit='B',unit_scale=True,
            )
            with open(file_path,'wb') as f:
                for data in res.iter_content(chunk_size=chunk_size):
                    if data:
                        f.write(data)
                        progress_bar.update(chunk_size)
            progress_bar.close()
    else:
        logging.error('download fail.')
        return False
