#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-14 14:45:22
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   :


from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import Required,Email,Length,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

# 登录表单
class LoginForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Email()])
    pwd = PasswordField('password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login IN')

# 注册表单
class RegisterForm(FlaskForm):
    username = StringField('UserName:',validators=[Required(),
        Regexp('^[\u4e00-\u9fa5_a-zA-Z0-9]*$',0,'用户名只能为英文数字中文')])
    password = PasswordField('PassWord:',validators=[Required()])
    # 通过EqualTo实现判断密码是否相同
    repassword = PasswordField('Confrm PassWord:',validators=[Required(),
        EqualTo('password',message='Password must match')])
    # 通过Email()实现判断邮箱合法性
    email = StringField('Email:',validators=[Required(),Length(1,64),Email()])
    submit = SubmitField('Register')

    # 如果表单类中定义了以validate_开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    # 判断email和User是否存在
    def validate_email(self,field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email already registered.')
    def validate_username(self,field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('UserName already in use.')

# 改密码
class ChangePasswordForm(FlaskForm):
    oldpassword = PasswordField('Old PassWord:',validators=[Required()])
    newpassword = PasswordField('New PassWord:',validators=[Required()])
    # 通过EqualTo实现判断密码是否相同
    repassword = PasswordField('Confrm PassWord:',validators=[Required(),
        EqualTo('newpassword',message='Password must match')])
    submit = SubmitField('Register')

# 重置密码，先输入邮箱
class ResetPassowrdRequeitForm(FlaskForm):
    email = StringField('Email:',validators=[Required(),Length(1,64),Email()])
    submit = SubmitField('Register')

# 重置密码，输入新密码
class ResetPassowrdForm(FlaskForm):
    password = PasswordField('New PassWord:',validators=[Required()])
    # 通过EqualTo实现判断密码是否相同
    repassword = PasswordField('Confrm PassWord:',validators=[Required(),
        EqualTo('password',message='Password must match')])
    submit = SubmitField('Register')


        
# 更改邮箱
class ChangeEmailForm(FlaskForm):
    email = StringField('New Email:',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Input your PassWord:',validators=[Required()])
    submit = SubmitField('Register')
