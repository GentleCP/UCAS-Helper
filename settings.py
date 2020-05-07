# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : settings.py
# @Item    : PyCharm
# @Time    : 2019-11-18 15:48
# @WebSite : https://www.gentlecp.com


# 填写你自己的用户信息
USER_INFO = {
    'username': '',
    'password': '',
    'remember': 'undefined'  # 此处不要动
}
SOURCE_DIR = '/Users/dongchaopeng/Documents/学习资料/UCAS-sources'

# ------------------后面的不要动--------------#

ACCOUNTS_PATH = 'accounts.json'
URLS = {
    'base_url':'https://jwxk.ucas.ac.cn',
    'login_url': 'http://onestop.ucas.ac.cn/Ajax/Login/0',
    'logout_url': 'http://sep.ucas.ac.cn/logout?o=platform',
    'course_info_url': 'http://sep.ucas.ac.cn/portal/site/16/801',
    'grade_url':'https://jwxk.ucas.ac.cn/score/yjs/all',
    'course_select_url': 'http://sep.ucas.ac.cn/portal/site/226/821',
}

# Assess message
ASSESS_MSG = [
    '这门课讲的真是太好了，我简直没有其他言语可以形容它！！！！',  # 这门课我最喜欢什么
    '我认为这门课做的很好了，课程内容一级棒！！！！！！',  # 我认为本课程应从哪些方面需要进一步改进和提高？
    '我平均每周都认认真真准备这门课的内容，每天超过4小时！！！',  # 我平均每周在这门课程上花费多少小时？
    '我对这个学科领域兴趣甚厚，有如滔滔江水，连绵不绝！！！！',  # 在参与这门课之前，我对这个学科领域兴趣如何
    '我每周都认认真真上课，生怕错过任何一堂课，在课堂上积极发言，踊跃举手，是全班的表率！！！！',  # 我对该课程的课堂参与度（包括出勤、回答问题等）
    '我觉得这个老师讲课十分有趣，课堂氛围十分活跃，是我喜欢的地方！',  # 这位老师的教学，你最喜欢什么？
    '老师简直完美，我对老师的敬仰犹如滔滔江水，连绵不绝！！！！'  # 您对老师有哪些意见和建议？
]


# Do not download list
FILTER_LIST = [
    '没啥卵用课-1 19-20春季',
    '有点卵用课-2 19-20春季',  # 多个之间逗号隔开，务必输入课程全称！
]