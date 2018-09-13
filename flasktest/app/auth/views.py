#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-13 09:16:16
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   :

# 安装的包
from flask import render_template,redirect,flash,request,url_for,session
from flask_login import login_required,login_user,logout_user
from flask_login import current_user
from datetime import datetime
# 本程序中的包
from . import auth
from ..models import User
from .forms import LoginForm
from .forms import RegisterForm
from .forms import ChangePasswordForm
from app import db
from ..email import send_mail

from .forms import ResetPassowrdRequeitForm
from .forms import ResetPassowrdForm
from .forms import ChangeEmailForm



# 登录页面
@auth.route('/login',methods = ['GET','POST']) 
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(email = form.email.data).first()
        # 如果用户存在且密码正确就登录
        if user is not None and user.check_password(form.pwd.data):
            # flask-login中的login_user()可以标记用户的登录状态为已登录。
            # login_user有一个remember的布尔型的值
            # 如果为False则关闭浏览器就退出登录，如果为True则记录在cookies中，下次直接登录。
            # 这里通过form.remember_me.data传递该值为True或者False
            login_user(user,form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html',form = form)

# 退出登录
@auth.route('/logout')
# @login_required为保护路由，保证只有认证登录的用户才可以访问
@login_required
def logout():
    # flask-login中的logout_user()用来退出登录，删除并重设用户会话
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# 注册页面视图
@auth.route('/register',methods = ['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data,
            password=form.password.data,
            datetime=datetime.now())
        db.session.add(user)
        db.session.commit()
        # 生成token,然后把token通过send_mail生成链接发送到用户邮箱
        token = user.generate_confirmation_token()
        send_mail(user.email,'Congratulations on your successful registration.','auth/email/confirm',user=user,token=token)
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

# 注册用户认证，通过邮件连接点击进入
# 需要用户先登录网站，然后点击注册时系统发送的确认邮件的链接或者复制邮件的链接到浏览器中打开。
# 从而把用户的状态更改为True，使得账户生效。
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    # 判断登录用户是否已经认证
    if current_user.confirmed:
        return redirect(url_for('main.index'))
        # 解析token，判断结果是否和数据库中的一样
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

# 判断是否为认证用户，防止没有认证的用户访问其他页面
# 只有认证了的用户才可以正常访问页面，没有认证的只可以访问特定页面
# 通过before_request和before_app_request修饰器可以实现该功能
# before_request ：只能应用到属于蓝本的请求上
# before_app_request ： 在蓝本中使用针对程序全局的请求
@auth.before_app_request
def before_request():
    # 如果用户登录 且没有认证 且不是访问auth蓝图下的页面和不是访问静态文件就跳转到unconfirmed页面进行认证
    # before_app_request满足一下条件就会被拦截：
    # 1. 用户已登录
    # 2. 没有认证的用户
    # 3.请求的端点不在认证认证蓝本中
    # 4.不是访问静态文件
    if current_user.is_authenticated \
    and not current_user.confirmed \
    and request.blueprint != 'auth' \
    and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

# 没有认证的跳转到这个页面进行发邮件认证
@auth.route('/unconfirmed')
def unconfirmed():
    # 如果用户不是普通用户或者已经认证了就跳转到首页
    # is_anonymous默认为False
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


# 重新发认证邮件
@auth.route('/confirm')
def resend_confirmation():
    # 通过current_user生成token，发送邮件
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,'Congratulations on your successful registration.','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

# 修改密码，要先登录才可以操作
@auth.route('/changepassword',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    # 判断是否为认证用户
    if current_user.confirmed:
        if form.validate_on_submit():
            # 判断旧密码是否正确，如果为正确则更新新密码
            if current_user.check_password(form.oldpassword.data):
                current_user.password = form.newpassword.data
                db.session.add(current_user)
                db.session.commit()
                flash('Reset Password successful.')
                return redirect(url_for('auth.change_password'))
            else:
                flash('Old Password is not True.')
    else:
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/changepassword.html',form=form)


# 忘记密码，需要重置密码
# 先输入邮件地址，判断邮箱是否已注册，然后生成一个token发到邮箱
@auth.route('/resetpasswordreq',methods=['GET','POST'])
def reset_password_request():
    form = ResetPassowrdRequeitForm()
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_token()
            send_mail(user.email,'Reset your Passowrd','auth/email/resetpwd',token=token,user=user)
            flash('The Reset password mail is send to your email.')
            return redirect(url_for('auth.login'))
        else:
            flash('The user could not be found.')
    return render_template('auth/resetpassword.html',form=form,label='please input your email.')

# 通过点击邮箱的链接，获取token，通过解析token获取用户id，然后更新输入的新密码
@auth.route('/resetpassword/<token>',methods=['GET','POST'])
def reset_password(token):
    form = ResetPassowrdForm()
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        if User.resetpassword(token,form.password.data):
            db.session.commit()
            flash('Reset Passowrd is successful.')
            return redirect(url_for('auth.login'))
    return render_template('auth/resetpassword.html',form=form,label='Reset password')

# 更改邮箱请求
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.email.data
        # 判断邮箱是否存在
        if User.query.filter_by(email=new_email).first() !=None:
            flash('The Mail is already exists.')
            return redirect(url_for('auth.change_email_request'))
        # 判断密码是否正确
        if current_user.check_password(form.password.data):
            # 生成token
            token = current_user.generate_email_change_token(new_email)
            # 发送邮件
            send_mail(new_email,'Change your Email','auth/email/change_email',token=token,user=current_user)
            flash('The change  mail is send to your new email.')
            return redirect(url_for('auth.change_email_request'))
        else:
            flash('password is wrong.')
            return redirect(url_for('auth.change_email_request'))
    # 这里的status是因为changemail.html页面中做了判断，如果等于status等于1则显示表单，不等于1则显示其他内容
    return render_template('auth/changemail.html',form=form,label='Change your email.',status=1)
# 更改邮箱确认，点击邮箱中的邮件链接
@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    # 判断token是否正确，更新是否成功
    if current_user.change_email(token):
        # 提交到数据库
        db.session.commit()
        return render_template('auth/changemail.html',status=0)
    else:
        flash('If the change is not successful, please revise it.')
        return redirect(url_for('auth.change_email_request'))

