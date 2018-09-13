#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-01 16:38:22
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 数据库表格模型

from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask import current_app

# 权限类，数字为对应权限的位值,类中是以十进制表示
class Permission:
    # 关注用户
    FOLLOW = 1
    # 发表评论
    COMMENT = 2
    # 写文章
    WRITE = 4
    # 管理他们发表的评价
    MODERATE = 8
    # 管理员权限
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    # 角色名
    name = db.Column(db.String(64), unique=True)
    # 设置默认角色
    default = db.Column(db.Boolean, default=False, index=True)
    # 权限
    permissions = db.Column(db.Integer)
    # db.relationship与User建立反向关系,backref='role'的值为自定义
    #backref 参数向 User 模型中添加一个 role 属性,从而定义反向关系。
    #这一属性可替代 role_id 访问 Role 模型,此时获取的是模型对象,而不是外键的值。
    #lazy属性决定加不加载纪录，dynamic是指不加载纪录但是提供查询
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        # 继承父类
        super(Role, self).__init__(**kwargs)
        # 如果自身权限为None则让其等于0
        if self.permissions is None:
            self.permissions = 0

    # 添加角色到数据库的类，设置成静态方法，可以直接调用
    # 直接在 python manage.py shell中运行Role.insert_roles()就可以添加了
    @staticmethod
    def insert_roles():
        # 设置角色和所拥有的权限
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        # 设置默认角色为User，默认注册的用户都是User
        default_role = 'User'
        # 遍历roles字典
        for r in roles:
            # 在数据库中查找roles字典中的KEY是否存在，如果没有则添加
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # 添加数据
                role = Role(name=r)
            # 把获取到的数据库中数据的permissions字段的字重置为0
            role.reset_permissions()
            # 遍历roles字典获取的key对应的values
            for perm in roles[r]:
                # 把值累加，得到这个角色所拥有权限的位值
                role.add_permission(perm)
            # 如果获取的role的name等于default_role，则为True
            # 则该数据数据库中的default为True，这里的default_role为User，所有只有User为True
            role.default = (role.name == default_role)
            # 每次循环的最后，添加或者更新数据到数据库
            db.session.add(role)
        # 提交到数据库，完成更新
        db.session.commit()

    # 添加权限
    def add_permission(self, perm):
        # 判断权限是否有，如果没有就添加
        # 没有权限时，self.has_permission(perm)返回是False，然后not False等于True
        if not self.has_permission(perm):
            self.permissions += perm

    # 删除权限
    def remove_permission(self, perm):
        # 判断权限是否有，如果有就删除
        # 这里self.has_permission(perm)返回True则为有权限
        if self.has_permission(perm):
            self.permissions -= perm

    # 重置权限为0
    def reset_permissions(self):
        self.permissions = 0

    # 判断当前角色是否已经有该权限
    def has_permission(self, perm):
        # 这里self.permissions默认为0
        # 这里用到位运算符&
        # & 按位与运算符：参与运算的两个值,如果两个相应位都为1,则该位的结果为1,否则为0
        # self.permissions & perm的值等于perm则为True
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name

# 继承多一个类UserMixin
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 用户名
    username = db.Column(db.String(255), unique=True, index=True)
    # 外键 db.ForeignKey()的参数 'roles.id' 表 明,这列的值是 roles 表中行的 id 值。
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 加密的密码
    password_hash = db.Column(db.String(255))
    # 邮箱
    email = db.Column(db.String(255), unique=True, index=True)
    # 录入时间
    datetime = db.Column(db.DateTime())
    # 是否认证用户，默认为Flase
    confirmed = db.Column(db.Boolean(),default=False)


    def __init__(self, **kwargs):
        # 继承父类
        super(User, self).__init__(**kwargs)
        # 判断当前用户的权限是否为空
        # 这里的role是上面Role中与User建立的反向关系时backref参数的值
        # 用户可以通过role查询Role中对应role_id的数据。
        if self.role is None:
            # 如果用户的email和配置中的FLASKY_ADMIN邮箱一样，则role的权限为管理员
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            # 经过上一步之后再判断role是否为空，如果空的就把default设置为True，作为普通用户
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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

    # 检查用户是否有权限操作，如果有权限则返回True
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    # 因为检查管理员权限经常用到，所以单独建立一个方法，方便使用
    # 检查其他权限的也可以单独建一个方法
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return '<User %r>' % self.username
# 新建一个AnonymousUser类方法，继承Flask-Login中的AnonymousUserMixin类
# 该类用于判断没有登录时候的用户权限，所以重写can和is_administrator方法返回值为False
# 这样就可以在用户没有登录情况下调用类方法，实现没有登录时候没有权限。
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
# 创建未登录用户的回调
# 未登录状态的匿名用户会调用AnonymousUser类，获取其权限为False
login_manager.anonymous_user = AnonymousUser

# 回调函数，使用指定的标识符加载用户。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))