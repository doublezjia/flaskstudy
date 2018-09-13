#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-07-26 16:21:56
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 配置文件

import os
# 获取当前文件所在的目录的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 基本配置
class Config():
    SECRET_KEY= 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT = 'Congratulations on your successful registration.'
    MAIL_SENDER = 'abc@qq.com'

    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')


    #此注释可表明使用类名可以直接调用该方法
    @staticmethod 
    # 执行当前需要的环境的初始化
    def init_app(app):
        pass
# 开发环境
class DevelopmentConfig(Config):
    """docstring for DevelopmentConfig"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@192.168.106.135:3306/flasktest'

# 生产环境
class ProductionConfig(Config):
    """docstring for ProductionConfig"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@192.168.106.135:3306/website'

# 测试环境
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@192.168.106.135:3306/webtest'

# config字典，方便后面使用
config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'testing': TestingConfig,
    'default':DevelopmentConfig
}
        