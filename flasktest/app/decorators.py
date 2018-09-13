#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-09-13 14:17:52
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id\
# @Desc       :自定义修饰器，用来检查常规权限和管理员权限

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

# 检查用户权限
# 修饰器使用了functools包中的wraps，如果用户没有权限则返回403
# 所以需要参考404错误编写自定义错误页面
def permission_required(permission):
    def decorator(f):
        # wraps的作用是不改变使用装饰器原有函数的结构(如__name__, __doc__)
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                # 返回错误代码403
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 检查管理员权限
def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

