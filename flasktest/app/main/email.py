#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-16 14:23:12
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   :

from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app,msg):
    # Flask-Mail中的send()函数使用cur-rent_app，因此要在激活的程序上下文中执行。
    with app.app_context():
        mail.send(msg)

def send_mail():
    app = current_app._get_current_object()
    # Message:邮件消息，sender：发送者邮箱；recipients：接收者邮箱，列表格式；body：内容
    msg = Message(subject='Hello World',sender='757147821@qq.com',recipients=[to])
    #邮件内容可以包含主体以及/或者 HTML
    msg.body = 'sended by flask-mail'
    msg.html = '<h1>test test test !!!!</h1>'
    
    # 异步发送邮件
    thread = Thread(target=send_async_email,args=[app,msg])
    thread.start()

    return thread
