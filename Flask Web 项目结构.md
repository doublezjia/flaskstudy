# Flask Web 项目结构

## 项目结构目录

Flask Web的项目结构如下

```
| - projectName
	| - app  //程序包
		| - templates //jinjia2模板
		|- static //css,js 图片等静态文件
		| - main  //py程序包 ，可以有多个这种包，每个对应不同的功能
			| - __init__.py
			|- errors.py
			|- forms.py
			|- views.py
		|- __init__.py
		|- email.py //邮件处理程序
		|- models.py //数据库模型
	|- migrations //数据迁移文件夹
	| - tests  //单元测试
		|- __init__.py
		|- test_basics.py //单元测试程序，可以包含多个对应不同的功能点测试
	|- venv  //虚拟环境,可以通过virtualenv生成
	|- requirements.txt //列出了所有依赖包以及版本号，方便在其他位置生成相同的虚拟环境以及依赖
	|- config.py //全局配置文件，配置全局变量
	|- manage.py //启动程序
```

一般包含程序包`app`，数据迁移文件夹`migrations`，全局配置文件`config.py`和启动文件`manage.py`


## 全局配置文件

`config.py`代码：
```
import os
# 获取当前文件所在的目录的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 基本配置
class Config():
    SECRET_KEY= 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    #此注释可表明使用类名可以直接调用该方法
    @staticmethod 
    # 执行当前需要的环境的初始化
    def init_app(app):
        pass
# 开发环境
class DevelopmentConfig(Config):
    """docstring for DevelopmentConfig"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@192.168.43.140:3306/flasktest'

# 生产环境
class ProductionConfig(Config):
    """docstring for ProductionConfig"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@192.168.43.140:3306/website'

# 测试环境
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@192.168.43.140:3306/test'

# config字典，方便后面使用
config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'testing': TestingConfig,
    'default':DevelopmentConfig
}
```

通过全部配置文件，把通用的基本配置先写在基类`Config`中，然后根据不同的运行环境新建类，继承基类并在其中写入对应环境需要的配置。最后在字典中添加，以便后面程序包中使用配置。

## 程序包

程序包用来保存程序的所有代码、模板和静态文件。我们可以把这个包直接称为app（应用），如果有需求，也可使用一个程序专用名字。

程序包根目录下包含存放网页的`templates`、存放静态文件的`static`和存放视图函数、蓝本等程序的`main`三个文件夹，以及邮件处理程序`email.py`和数据模型`models.py`

在单个文件中开发程序因为在全局作用域中创建，所以不能动态修改配置。要实现动态修改配置，就要延迟创建程序实例，所以新建一个函数，把创建程序实例的过程添加到这个函数中，然后在使用中通过调用这个函数实现程序实例初始化。


### 使用工厂函数

函数写在`app/__init__.py`中，如果没有就新建一个，把需要用到的Flask扩展的包在这里引入。

`app/__init__.py`代码：
```
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()

#创建实例初始化函数
def create_app(config_name):
    app = Flask(__name__)
    # 可以直接把对象里面的配置数据转换到app.config里面
    app.config.from_object(config[config_name])
    # 这里的init_app是config中的方法
    config[config_name].init_app(app)

    # 这里的init_app是Flask扩展自带的初始化方法
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    # 注册蓝本，用于后面路由和自定义页面处理
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

```

## 通过蓝本实现程序功能

因为现在程序是运行时创建实例，通过调用`create_app()`才可以使用`app.route`和`app.errorhandler`修饰器，这是定义路由就晚了，所以这里用用到蓝本来实现定义路由。

通过蓝本定义的路由是处于休眠状态的，直到蓝本注册到程序中，路由才会成为程序的一部分，使用位于全局作用域中的蓝本时，定义路由的方法几乎和单脚本程序一样。

和程序一样，蓝本可以在单个文件中定义，也可使用更结构化的方式在包中的多个模块中创建。为了获得最大的灵活性，程序包中创建了一个子包，用于保存蓝本。

`app/main/__init__.py`代码：

```
from flask import Blueprint

# Blueprint必须指定两个参数，蓝本的名称和蓝本所在的包或模块
# 第一个自定义，第二个默认情况下用__name__即可
main = Blueprint('main',__name__)

# views.py errors.py都在这个目录下，导入视图等模块，与蓝本关联起来
# 注意的是这些views.py模块要在最后导入，因为模块中会用到蓝本main，在最后导入可以避免出错
from . import views,errors
```

在工厂函数中的最后导入蓝本

```
def create_app(config_name):
#.......

    # 注册蓝本，用于后面路由和自定义页面处理
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
```


### 自定义错误处理和路由程序写法

#### 自定义错误处理

在蓝本中编写错误处理程序稍有不同，如果使用`errorhandler`修饰器，那么只有蓝本中的错误才能触发处理程序。要想注册程序全局的错误处理程序，必须使用`app_errorhandler`。

errors.py代码示例
```
from flask import render_template

from . import main

#这里注册全局错误处理，要使用app_errorhandler
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
```

#### 视图

views.py代码示例
```
from flask import render_template,session,url_for,session,flash,redirect

from . import main
from .forms import Nameform
from ..models import User
from .. import db


@main.route('/',methods = ['GET','POST'])
def index():
    form = Nameform()
    if form.validate_on_submit():
        session['user'] = form.user.data
        # 添加到数据库
        user = User(username=form.user.data)
        db.session.add(user)
        db.session.commit()   
        # 重定向到页面,这里要注意要用main.index或者.index
        return redirect(url_for('main.index'))
    return render_template('index.html',user=session.get('user'),form = form)
```

> 注意这里蓝本使用url_for重定向时要写`main.index`或者`.index`


### 启动脚本

manage.py代码示例

```
# 导入包
from app import create_app,db 
from app.models import Role,User
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

#创建对象
app = create_app('production')

manager = Manager(app)

migrate = Migrate(app,db)

#集成python shell
#为Python shell 添加一个上下文，这样就可以不用每次运行shell都要导入这些包
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

#迁移仓库相关，附加db命令到Flask-Script的manager对象上
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
```

### 需求文件

为了方便可以在其他环境中正常运行，所以需要生成一个`requirements.txt`，记录本环境中的所有依赖包。

这个文件可以通过命令生成：
```
pip freeze > requirements.txt
```

这样就可以把当前环境中安装的包和版本都记录下来了

然后在新的环境上运行以下命令就可以安装了。
```
pip install -r requirements.txt
```

### 单元测试

#### 测试代码

本例中的单元测试`tests/test_basics.py`代码:
```
import unittest
from flask import current_app
from app import create_app, db


# 这个测试使用Python标准库中的unittest包编写
# setUp()和tearDown()方法分别在各测试前后运行，并且名字以test_开头的函数都作为测试执行。

class BasicsTestCase(unittest.TestCase):
    # setUp()方法尝试创建一个测试环境，类似于运行中的程序。
    def setUp(self):
        # 创建程序实例
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        # app_context.push() 把上下文记录下来
        self.app_context.push()
        # 创建表
        db.create_all()

    # 测试的最后用通过tearDown删除setUp创建的内容
    def tearDown(self):
        # 删除表
        db.session.remove()
        db.drop_all()
        # app_context.pop() 把上下文移除
        self.app_context.pop()

    # 这个测试用来测试程序实例是否存在
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    # 这个测试用来确保程序在测试配置中运行.
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
```

这个测试使用Python标准库中的`unittest`包编写。`setUp()`和`tearDown()`方法分别在各测试前后运行，并且名字以`test_`开头的函数都作为测试执行。

`setUp()`方法尝试创建一个测试环境，类似于运行中的程序。首先，使用测试配置创建程序，然后激活上下文。这一步的作用是确保能在测试中使用`current_app`，像普通请求一样。然后创建一个全新的数据库，以备不时之需。数据库和程序上下文在`tearDown()`方法中删除。

代码创建了两个测试实例，第一个测试确保程序实例存在。第二个测试确保程序在测试配置中运行。若想把`tests文件夹`作为包使用，需要添加`tests/__init__.py`文件，不过这个文件可以为空，因为`unittest`包会扫描所有模块并查找测试。

#### 启动测试

为了可以运行单元测试，需要先在`manager.py`中添加一个自定义命令

代码：
```
# 为了运行单元测试，在这里添加自定义命名test，运行的时候输入python manager.py test就可以了
@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
```

`manager.command`修饰器让自定义命令变得简单。修饰函数名就是命令名，函数的文档字符串会显示在帮助消息中。`test()`函数的定义体中调用了`unittest`包提供的测试运行函数。


运行命令

```
python manager.py test
```

>flask 单元测试可以看看这个网站：[Flask之单元测试](https://www.2cto.com/kf/201807/761445.html)
>了解单元测试可以看看这里：[单元测试-廖雪峰](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/00143191629979802b566644aa84656b50cd484ec4a7838000)

### 创建数据库

因为这里使用了数据迁移，首先建立数据迁移仓库

```
python manager.py db init
```

然后创建迁移脚本

```
python manager.py db migrate
```

之后就可以通过upgrade更新数据模型到数据库了。

```
python manager.py db upgrade
```

>创建数据表前要先在数据库中新建一个数据库，如果表创建不成功的就进入Python shell 用`db.create_all()`创建表。

