#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-06 15:42:14
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 表单

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,TextAreaField,BooleanField,SelectField
from wtforms.validators import Required,Email,Length,Regexp
from wtforms import ValidationError
from ..models import Role,User


from flask_wtf.file import FileField, FileRequired, FileAllowed

class Nameform(FlaskForm):
    user = StringField('name',validators=[Required()])
    email = StringField('Email',validators=[Required(),Email()])
    pwd = PasswordField('password',validators=[Required()])
    submit = SubmitField('Submit')

# 用户修改信息表单
class EditProfileForm(FlaskForm):
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
        
# 管理员修改信息表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Email(),Length(1,64)])
    username = StringField('Username',validators=[Required(),Length(1,64),
        Regexp('^[\u4e00-\u9fa5_a-zA-Z0-9]*$',0,'用户名只能为英文数字中文')])
    confirmed = BooleanField('Confirmed')
    # 把值转为整数型
    role = SelectField('Role',coerce=int)
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        # role这个选择框的值和内容，通过Role在数据库中获取
        self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        # 把传入的user赋值到self.user中
        self.user = user

    # 判断修改的邮件是否已经存在
    def validate_email(self,field):
        # 如果修改的值跟原来的值不一样并且用户的值存在则提示
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    # 判断修改的用户名是否已经存在
    def validate_username(self,field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

# 上传文件
class FileUploadsForm(FlaskForm):
    fileUpload = FileField(u'图片上传', 
        validators=[FileAllowed(['jpg','gif','png','jpeg','bmp'], u'只能上传图片！'),
        FileRequired(u'图片未选择！')])
    submit = SubmitField('Submit')
        

# 富文本编辑器
class CkeditorForm(FlaskForm):
    title = StringField('标题',validators=[Required()])
    content = TextAreaField('正文')
    submit = SubmitField('Submit')