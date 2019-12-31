# @Author  : GentleCP
# @Email   : 574881148@qq.com
# @File    : ucashelper.py
# @Item    : PyCharm
# @Time    : 2019/11/28/028 13:58
# @WebSite : https://www.gentlecp.com

import sys
from core import main
from core.wifi import AccHacker

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main.main()

    elif len(sys.argv) > 1 and sys.argv[1] == 'hack':
        hacker = AccHacker(data_path='core/data.txt', password_path='core/password.txt')
        hacker.run()
