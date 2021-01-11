#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-----------------File Info-----------------------
            Name: configer.py
            Description: 初始配置器，引导配置
            Author: GentleCP
            Email: 574881148@qq.com
            WebSite: https://www.gentlecp.com
            Create Date: 2021-01-11 
-----------------End-----------------------------
"""

import npyscreen as nps


from settings import USER_CONFIG_PATH
from handler.exception import ExitStatus
from util.functions import get_cfg

WELCOME_DIALOG = ('Welcome to the UCAS Helper Config setting panel.\n\n'
                  'It will store your personal user information into local file:\'{}\'\n'
                  'Please select \'ok\' if you agree.'.format(USER_CONFIG_PATH))


class UCASHelperConfigMenu(nps.Form):
    EXTRA_KWARGS = []

    def __init__(self, *args, **keywords):
        self.next_form = keywords.get('next_form')
        self.action_on_ok = keywords.get('action_on_ok')

        [setattr(self, key, keywords.get(key)) for key in self.__class__.EXTRA_KWARGS]

        super(nps.Form, self).__init__(*args, **keywords)
        if self.name is None:
            self.name = 'UCAS-Helper configuration settings'


class UCASHelperConfigAF(nps.ActionFormV2, UCASHelperConfigMenu):
    OK_BUTTON_BR_OFFSET = (2, 14)
    CANCEL_BUTTON_BR_OFFSET = (2, 6)

    EXTRA_KWARGS = ['exit_on_cancel', 'action_on_ok']

    def on_ok(self):
        if self.action_on_ok:
            self.action_on_ok()
        if self.next_form:
            self.parentApp.setNextForm(self.next_form)
        else:
            exit(ExitStatus.OK)

    def on_cancel(self):
        if self.exit_on_cancel:
            exit(ExitStatus.OK)
        else:
            self.parentApp.setNextFormPrevious()



class UCASHelperConfigWarning(UCASHelperConfigAF):
    OK_BUTTON_TEXT     = "OK"
    CANCEL_BUTTON_TEXT = "EXIT"

    EXTRA_KWARGS = UCASHelperConfigAF.EXTRA_KWARGS + ['text']

    def create(self):
        self.add(nps.Pager, values=self.text.split('\n'),
                 autowrap=True, editable=False)


class UCASHelperConfigWarningPopup(nps.ActionPopup, UCASHelperConfigWarning):
    ''' Displays a warning as popup '''
    pass


class UCASHelperConfig(UCASHelperConfigAF):
    """
    The basic class of Config, other configuration classes inherit from it
    """
    OK_BUTTON_TEXT     = "OK"
    CANCEL_BUTTON_TEXT = "BACK"

    EXTRA_KWARGS = UCASHelperConfigAF.EXTRA_KWARGS + ['user_config_path', 'cfg', 'section']

    def create(self):
        pass


    def on_ok(self):
        if not self.input_texts:
            self.input_texts = {}
        if not self.cfg.has_section(self.section):
            self.cfg.add_section(self.section)

        if self.input_texts.keys():
            for key, value in self.input_texts.items():
                if value:
                    self.cfg.set(self.section, key, value)
            self.cfg.write(open(self.user_config_path, 'w'))
        super().on_ok()



class UCASHelperUserInfoConfig(UCASHelperConfig):
    """
    User Info config，Required
    """
    TIPs = '【Required】Enter your user info which is used to login sep website.'

    def create(self):
        super().create()
        self.add(nps.TitleText, name=self.__class__.TIPs, autowrap=True, editable=False)
        self.username = self.add(nps.TitleText, name='username')
        self.password = self.add(nps.TitlePassword, name='password')

    def on_ok(self):
        self.input_texts = {
            'username': self.username.value,
            'password': self.password.value

        }
        super().on_ok()


class UCASHelperDownloadConfig(UCASHelperConfig):
    """
    Download Resources Config, Optional
    """

    TIPs = ('【Optional】Enter the path where you want to store the course resources.(e.g. `D:/UCAS-resources`)\n')

    def create(self):
        super().create()
        self.add(nps.TitleText, name=self.__class__.TIPs, autowrap=True, editable=False)
        self.resource_path = self.add(nps.TitleText, name='resource path')


    def on_ok(self):
        self.input_texts = {
            'resource_path': self.resource_path.value
        }
        super().on_ok()


class UCASHelperConfigApp(nps.NPSAppManaged):

    STARTING_FORM = 'WelcomeDialog'


    def onStart(self):
        user_cfg = get_cfg(config_path=USER_CONFIG_PATH)
        self.addForm('WelcomeDialog', UCASHelperConfigWarningPopup,
                     text=WELCOME_DIALOG, exit_on_cancel=True,
                     next_form='UserInfoConfig',
                    )
        self.addForm('UserInfoConfig', UCASHelperUserInfoConfig,
                     user_config_path=USER_CONFIG_PATH,
                     cfg=user_cfg,
                     section='user_info',
                     next_form='DownloadConfig',
                     exit_on_cancel=False
                     )
        self.addForm('DownloadConfig', UCASHelperDownloadConfig,
                     user_config_path=USER_CONFIG_PATH,
                     cfg=user_cfg,
                     section='course_info',
                     exit_on_cancel=False)


if __name__ == '__main__':
    UCASHelperConfigApp().run()