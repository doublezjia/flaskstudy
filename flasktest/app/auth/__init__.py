#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-13 09:12:23
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   :

from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views
