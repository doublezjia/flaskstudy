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
from .forms import EditProfileForm
from .forms import EditProfileAdminForm
from ..models import User,Role
from .. import db

from flask_login import login_required
from flask_login import current_user
import datetime

from ..models import Permission
from ..decorators import permission_required
from ..decorators import admin_required

import json
# 管理员页面
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For administrators'

# 有moderate权限才可以访问
@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return 'For commit moderators!'

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

# 用户页面
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    # 如果没有这个用户，返回404
    if user is None:
        abort(404)
    return render_template('user.html',user=user)

# 用户信息修改
@main.route('/user/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
   form = EditProfileForm()
   if form.validate_on_submit():
       current_user.about_me = form.about_me.data
       db.session.add(current_user)
       flash('Your profile has been updated.')
       return redirect(url_for('main.user',username=current_user.username))
   form.about_me.data = current_user.about_me
   return  render_template('edit_profile.html',form=form)


@main.route('/admin/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    # get_or_404(id)通过id查找是否有这个用户，有就返回结果，没有就返回404
    user = User.query.get_or_404(id)
    # 传入user值到EditProfileAdminForm，用来判断修改的值跟原来的是否一样
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        # form.role.data的值为Role表对应的ID值
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')

        # 如果是管理员编辑其他人数据的就返回userlist这个页面
        if current_user.is_administrator and user.id != current_user.id:
            return redirect(url_for('main.userlist'))

        return redirect(url_for('main.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    # user.role_id为对应的Role表中的ID
    form.role.data = user.role_id
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)

# 用户列表
@main.route('/admin/userlist/')
@login_required
@admin_required
def userlist():
    # 查询所有数据
    userlist = User.query.order_by(User.id).all()
    return render_template('userlist.html',userlist=userlist)