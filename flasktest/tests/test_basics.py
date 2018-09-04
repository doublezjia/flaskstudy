#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-09 11:10:45
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   :

import unittest
from flask import current_app
from app import create_app, db
from app.email import send_mail


# 这个测试使用Python标准库中的unittest包编写
# setUp()和tearDown()方法分别在各测试前后运行，并且名字以test_开头的函数都作为测试执行。

class BasicsTestCase(unittest.TestCase):
    # setUp()方法尝试创建一个测试环境，类似于运行中的程序。
    def setUp(self):
        # 创建程序实例
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        # app_context.push() 把上下文记录下来
        self.app_context.push()
        # 创建表
        db.create_all()

    # 测试的最后用通过tearDown删除setUp创建的内容
    def tearDown(self):
        # 删除表
        db.session.remove()
        db.drop_all()
        # app_context.pop() 把上下文移除
        self.app_context.pop()

    # 这个测试用来测试程序实例是否存在
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    # 这个测试用来确保程序在测试配置中运行.
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])


