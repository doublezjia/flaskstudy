#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-01 16:29:41
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 启动脚本

import os

# 导入包
from app import create_app,db 
from app.models import Role,User,Permission,Article
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand


app = create_app('default')


manager = Manager(app)

migrate = Migrate(app,db)


#集成python shell
#为Python shell 添加一个上下文，这样就可以不用每次运行shell都要导入这些包
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Article=Article,Permission=Permission)
manager.add_command("shell", Shell(make_context=make_shell_context))

#迁移仓库相关，附加db命令到Flask-Script的manager对象上
manager.add_command("db", MigrateCommand)


# 为了运行单元测试，在这里添加自定义命名test，运行的时候输入python manager.py test就可以了
@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()