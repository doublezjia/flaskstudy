#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-07-30 14:30:27
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   :

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from config import config
from flask_mail import Mail
from threading import Thread
from flask_login import LoginManager

from flask_uploads import UploadSet, configure_uploads, IMAGES

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()

# flaks-uploads
# 设置UploadSet
photos = UploadSet('photos', IMAGES)

def create_app(config_name):
    app = Flask(__name__)
    # 可以直接把对象里面的配置数据转换到app.config里面
    app.config.from_object(config[config_name])
    # 这里的init_app是config中的方法
    config[config_name].init_app(app)



    # 这里的init_app是Flask扩展自带的初始化方法
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Flask-uploads
    # 使用configure_uploads()方法注册并完成相应的配置（类似大多数扩展提供的初始化类）
    # 传入当前应用实例和set
    configure_uploads(app, photos)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    

    return app

