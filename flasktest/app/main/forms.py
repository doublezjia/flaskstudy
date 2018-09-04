#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-06 15:42:14
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 表单

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import Required,Email

class Nameform(FlaskForm):
    user = StringField('name',validators=[Required()])
    email = StringField('Email',validators=[Required(),Email()])
    pwd = PasswordField('password',validators=[Required()])
    submit = SubmitField('submit')