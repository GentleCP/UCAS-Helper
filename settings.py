# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : settings.py
# @Item    : PyCharm
# @Time    : 2019-11-18 15:48
# @WebSite : https://www.gentlecp.com


# 填写你自己的用户信息
USER_INFO = {
    'username':'',
    'password':'',
    'remember':'checked'  # 此处不要动
}
SOURCE_DIR = 'D:/UCAS-courses'


#------------------后面的不要动--------------#

ACCOUNTS_PATH = 'accounts.json'
URLS = {
    'login_url' : 'http://onestop.ucas.ac.cn/Ajax/Login/0',
    'logout_url': 'http://sep.ucas.ac.cn/logout?o=platform',
    'course_info_url' : 'http://sep.ucas.ac.cn/portal/site/16/801',
    'scholarship_url' : 'http://sep.ucas.ac.cn/portal/site/282',
    'zlyh_url':'http://scholarship.ucas.ac.cn/gmjaward/GmjAlppyDetails_Xs?award_id=123',
    'gm_scholar_url':'http://scholarship.ucas.ac.cn/GmjAward/GmjList_Xs',
    'edit_zlyh_url':'http://scholarship.ucas.ac.cn/GmjAward/GmjAlppyEdit_Xs/12686'
}
