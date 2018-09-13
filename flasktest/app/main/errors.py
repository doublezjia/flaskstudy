#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-06 15:07:25
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 错误处理

from flask import render_template

from . import main

#这里注册全局错误处理，要使用app_errorhandler
@main.app_errorhandler(403)
def page_not_found(e):
    return render_template('403.html'),403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@main.app_errorhandler(500)
def page_not_found(e):
    return render_template('404.html'),500