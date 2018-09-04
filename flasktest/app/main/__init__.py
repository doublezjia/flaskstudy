#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-01 16:00:52
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : Flask蓝本

from flask import Blueprint

# Blueprint必须指定两个参数，蓝本的名称和蓝本所在的包或模块
# 第一个自定义，第二个默认情况下用__name__即可
main = Blueprint('main',__name__)

# views.py errors.py都在这个目录下，导入视图等模块，与蓝本关联起来
# 注意的是这些views.py模块要在最后导入，因为模块中会用到蓝本main，在最后导入可以避免出错
from . import views,errors