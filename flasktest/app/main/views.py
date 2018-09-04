#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-01 16:24:50
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 网站视图

from flask import render_template,session,url_for,session,flash,redirect

from . import main
from .forms import Nameform
from ..models import User
from .. import db

import datetime

@main.route('/',methods = ['GET','POST'])
def index():
    form = Nameform()
    session['user'] = form.user.data
    if form.validate_on_submit():
        session['user'] = form.user.data
        # 添加到数据库
        user = User.query.filter_by(username=form.user.data).first()
        if user is None:
            user = User(username=form.user.data,email = form.email.data,password=form.pwd.data,datetime=datetime.datetime.now())
            db.session.add(user)
            db.session.commit()   
            flash('add a user')
        else :
            pass
            # if user.check_password(form.pwd.data) is True:
            #     flash('password is right')
            # else:
            #     flash('passowrd is wrong')
        # 重定向到页面,这里要注意要用main.index或者.index
        return redirect(url_for('.index'))
    return render_template('index.html',user=session.get('user'),form = form)
