# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : settings.py
# @Item    : PyCharm
# @Time    : 2019-11-18 15:48
# @WebSite : https://www.gentlecp.com


# 根据你个人喜好修改评估的内容
ASSESS_MSG = [
    '这门课讲的真是太好了，我简直没有其他言语可以形容它！！！！',  # 这门课我最喜欢什么
    '我认为这门课做的很好了，课程内容一级棒！！！！！！',  # 我认为本课程应从哪些方面需要进一步改进和提高？
    '我平均每周都认认真真准备这门课的内容，每天超过4小时！！！',  # 我平均每周在这门课程上花费多少小时？
    '我对这个学科领域兴趣甚厚，有如滔滔江水，连绵不绝！！！！',  # 在参与这门课之前，我对这个学科领域兴趣如何
    '我每周都认认真真上课，生怕错过任何一堂课，在课堂上积极发言，踊跃举手，是全班的表率！！！！',  # 我对该课程的课堂参与度（包括出勤、回答问题等）
    '我觉得这个老师讲课十分有趣，课堂氛围十分活跃，是我喜欢的地方！',  # 这位老师的教学，你最喜欢什么？
    '老师简直完美，我对老师的敬仰犹如滔滔江水，连绵不绝！！！！'  # 您对老师有哪些意见和建议？
]


# 不希望同步的课程内容，多个之间逗号隔开，务必输入课程全称！
FILTER_LIST = [
    '没啥卵用课-1 19-20春季',
    '有点卵用课-2 19-20春季',
]
#------------------------由用户决定的配置信息-----------------------------------



# ------------------后面的不要随意更改--------------



# PATH info
USER_CONFIG_PATH = '../conf/user_config.ini'
RECORD_PATH = '../conf/record.ini'  # 保存一些程序运行完毕后需要持久化存储到本地的信息
ACCOUNTS_PATH = '../accounts.json'

# USLs that used for request
URLS = {
    'home_url':{
        'http':'http://onestop.ucas.ac.cn/',
        'https':'https://onestop.ucas.ac.cn/'
    },
    'bak_home_url':{
        'http': 'http://sep.ucas.ac.cn/',
        'https': 'https://sep.ucas.ac.cn/'
    },
    'base_url':{
        'http':'http://jwxk.ucas.ac.cn',
        'https':'https://jwxk.ucas.ac.cn',
    },
    'login_url': {
        'http':'http://onestop.ucas.ac.cn/Ajax/Login/0',
        'https':'https://onestop.ucas.ac.cn/Ajax/Login/0'
    },
    'bak_login_url':{
        'http': 'http://sep.ucas.ac.cn/slogin',
        'https': 'https://sep.ucas.ac.cn/slogin'
    },
    'logout_url': {
        'http':'http://sep.ucas.ac.cn/logout?o=platform',
        'https':'https://sep.ucas.ac.cn/logout?o=platform',
    },
    'course_info_url': {
        'http':'http://sep.ucas.ac.cn/portal/site/16/801',
        'https':'https://sep.ucas.ac.cn/portal/site/16/801',
    },
    'grade_url':{
        'http':'http://jwxk.ucas.ac.cn/score/yjs/all',
        'https':'http://jwxk.ucas.ac.cn/score/yjs/all',
    },
    'view_url':{
        'http':'http://jwxk.ucas.ac.cn/notice/view/1',
        'https':'https://jwxk.ucas.ac.cn/notice/view/1',
    },
    'course_select_url': {
        'http':'http://sep.ucas.ac.cn/portal/site/226/821',
        'https':'https://sep.ucas.ac.cn/portal/site/226/821',
    },
    'base_saveCourseEval_url':{
        'http':'http://jwxk.ucas.ac.cn/evaluate/saveCourseEval/',
        'https':'https://jwxk.ucas.ac.cn/evaluate/saveCourseEval/',
    },
    'base_evaluateCourse_url':{
        'http':'http://jwxk.ucas.ac.cn/evaluate/evaluateCourse/',
        'https':'https://jwxk.ucas.ac.cn/evaluate/evaluateCourse/',
    },
    'base_evaluateTeacher_url':{
        'http':'http://jwxk.ucas.ac.cn/evaluate/evaluateTeacher/',
        'https':'https://jwxk.ucas.ac.cn/evaluate/evaluateTeacher/'
    }
}
