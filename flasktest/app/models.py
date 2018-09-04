#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-01 16:38:22
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 数据库表格模型

from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask import current_app


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name

# 继承多一个类UserMixin
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 用户名
    username = db.Column(db.String(255), unique=True, index=True)
    # 加密的密码
    password_hash = db.Column(db.String(255))
    # 邮箱
    email = db.Column(db.String(255), unique=True, index=True)
    # 录入时间
    datetime = db.Column(db.DateTime())
    # 是否认证用户，默认为Flase
    confirmed = db.Column(db.Boolean(),default=False)

    # 加密密码
    # @property 把password方法变为User的属性，只读
    @property
    def password(self):
        # 设置不能直接读取密码
        raise AttributeError('password is not a readable attribute')
    # @password.setter 把password变为一个可以赋值的属性
    # 写入密码，同时计算hash值，保存到模型中
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    # 检查密码是否正确
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    # 生成确认令牌
    # 认证用户
    # 生成令牌
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    # 解析令牌，认证
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False 
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True


    # 忘记密码
    # 生成token
    def generate_password_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'id':self.id})
    # 解析token,更新密码
    def resetpassword(token,newpassword):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        user = User.query.filter_by(id=data.get('id')).first()
        if user is None:
            return False
        user.password = newpassword
        db.session.add(user)
        return True

    # 更改邮箱
    #生成token
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')
    # 解析token，更新邮箱
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


# 回调函数，使用指定的标识符加载用户。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))