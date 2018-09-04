# Flask Web开发笔记



## Python虚拟环境

>虚拟环境有virtualenv和Anaconda

虚拟环境非常有用，可以在系统的Python解释器中避免包的混乱和版本的冲突。为每个程序单独创建虚拟环境可以保证程序只能访问虚拟环境中的包，从而保持全局解释器的干净整洁，使其只作为创建（更多）虚拟环境的源。使用虚拟环境还有个好处，那就是不需要管理员权限。

virtualenv安装：
```
Ubuntu:
sudo apt-get install python-virtualenv
```

创建虚拟环境：
```
默认为Python2，所以直接创建就可以了
virtualenv venv

如果是Python3，-p 然后指定Python3命令路径 然后加虚拟环境名，前提是系统已经安装了Python3
virtualenv -p /usr/bin/python3 py3env

```

运行：
```
linux或者Mac OX
source venv/bin/activate

Windows：
venv\Scripts\activate
```

退出：
```
deactivate
```

>Anaconda的可以到这个网站现在安装 [https://www.anaconda.com/download/](https://www.anaconda.com/download/)

## Flask
>使用环境：Python3.x

安装：
```
pip install flask
```

### 使用

先创建程序实例
```
from flask import Flask
app = Flask(__name__)
```
使用程序实例提供的`app.route`修饰器，把修饰的函数注册为路由
```
@app.route('/')
def index():    
	return '<h1>Hello World!</h1>'
```
定义的路由中就有一部分是动态名字：
```
@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name
```
尖括号中的内容就是动态部分，任何能匹配静态部分的URL都会映射到这个路由上。调用视图函数时，Flask会将动态部分作为参数传入函数。在这个视图函数中，参数用于生成针对个人的欢迎消息。


路由中的动态部分默认使用字符串，不过也可使用类型定义。例如，路由`/user/<int:id>`只会匹配动态片段`id`为整数的URL。Flask支持在路由中使用`int`、`float`和`path`类型。path类型也是字符串，但不把斜线视作分隔符，而将其当作动态片段的一部分。
 
启动服务器

```
if __name__ == '__main__':
    app.run(debug=True)
```
>要想启用调试模式，我们可以把`debug`参数设为`True`。


这样一个简单的Flask程序好了，然后保存Python文件并运行。就可以通过浏览器输入`http://127.0.0.1:5000`打开web


### 程序和请求上下文

|变量名|上下文|说明|
|-----|-----|----|
|current_app|程序上下文|当前激活程序的程序实例|
|g|程序上下文|处理请求时用作临时存储的对象，每次请求都会重设这个变量|
|requests|请求上下文|请求对象，封装了客户端发出的HTTP请求中的内容|
|session|请求上下文|用户会话，用于存储请求之间需要‘记住’的值的词典|

Flask在分发请求之前激活（或推送）程序和请求上下文，请求处理完成后再将其删除。程序上下文被推送后，就可以在线程中使用current_app和g变量。类似地，请求上下文被推送后，就可以使用request和session变量。如果使用这些变量时我们没有激活程序上下文或请求上下文，就会导致错误。


## Flask扩展

Flask-Script是一个Flask扩展，为Flask程序添加了一个命令行解析器。Flask-Script自带了一组常用选项，而且还支持自定义命令。

安装：

```
pip install flask-script
```

使用：
```
from flask_script import Manager

app = Flask(__name__)
manager = Manager(app)

if __name__ == '__main__':
	manager.run()
```

运行：

```
python hello.py runserver --host 0.0.0.0
```
这样其他电脑也可以通过ip进行访问。


## Flask模板

Flask使用了一个名为Jinja2的强大模板引擎。

使用时要先在程序的根目录下新建一个templates的文件夹，并在里面创建html文件。然后在程序中引入`render_template`

例子：

```
from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

if __name__ == '__main__':
	app.run(debug=True)
```

然后在user.html页面中添加一个`{{name}}`这样的变量，这样就可以把name这个值传递到页面中。

HTML中的代码：
```
<h1>hello,{{name}}</h1>
```

Jinja2中使用{{name}}结构表示一个变量，它是一种特殊的占位符，告诉模板引擎这个位置的值从渲染模板时使用的数据中获取。

Jinja2能识别所有类型的变量，甚至是一些复杂的类型，例如列表、字典和对象。

Jinja2可以使用过滤器修改变量，过滤器名添加在变量名之后，中间使用竖线分隔。

例如以首字母大写形式显示变量name的值：
```
Hello, {{ name|capitalize }}
```

Jinja2变量过滤器表:

|过滤器名|说明|
|------|--------|
|safe|渲染值时不转义|
|capitalize|首字母大写|
|lower|把值转换为小写|
|upper|把值转换为大写|
|title|把值中每个单词的首字母转换为大写|
|trim|把值的首尾空格去掉|
|striptage|渲染之前把值中的所有HTML标签都删掉|

>Jinja2会转义所有变量。所以要是输出HTML的时候要加上safe不转义。

>完整过滤器列表[http://jinja.pocoo.org/docs/templates/#builtin-filters](http://jinja.pocoo.org/docs/templates/#builtin-filters)

Jinja2支持判断、for循环和宏（宏就是类似Python中的函数）。

写法：
```
判断
{% if user %}
    Hello, {{ user }}!
{% else %}
    Hello, Stranger!
{% endif %}

for循环
{% for comment in comments %}
        {{ comment }}
{% endfor %}

宏
{% macro render_comment(comment) %}
    <li>{{ comment }}</li>
{% endmacro %}
<ul>
    {% for comment in comments %}
        {{ render_comment(comment) }}
            {% endfor %}
</ul>
```

需要重复使用的模板代码可以先把代码写在单独的文件。
然后通过`include`包含进去。
```
{%include 'name.html' %}
```

Jinja2支持模板的继承，所以可以创建一个基本的模板`base.html`，例如:
```
<html>
<head>
    {% block head %}
    <title>
	{% block title %}
    {% endblock %} - My Application
    </title> 
    {% endblock %}
</head>
<body>
    {% block body %}
    {% endblock %}
</body>
</html>
```

`block`标签定义的元素可在衍生模板中修改。在本例中，我们定义了名为`head`、`title`和`body`的块。注意，`title`包含在`head`中。下面这个示例是基模板的衍生模板：

```
{% extends "base.html" %}
{% block title %}Index{% endblock %}
{% block head %}
    {{ super() }}
    <style>    
    </style>
{% endblock %}
{% block body %}
    <h1>Hello, World!</h1>
{% endblock %}
```

extends指令声明这个模板衍生自`base.html`。在`extends`指令之后，基模板中的3个块被重新定义，模板引擎会将其插入适当的位置。注意新定义的`head`块，在基模板中其内容不是空的，所以使用`super()`获取原来的内容。


## Bootstrap

Bootstrap是个web的前端框架，可以通过页面引用CSS样式进行使用，也可以通过Flask-Bootstrap安装使用。

Flask-Bootstrap安装：
```
pip install flask-bootstrap
```
初始化：
```
from flask_bootstrap import Bootstrap
# ...
bootstrap = Bootstrap(app)
```
在HTML中继承
```
{% extends "bootstrap/base.html" %}
```

Flask-Bootstrap基模板中定义的块

|块名|说明|
|----|---|
|doc|整个HTML文档|
|html_attribs|&lt;html&gt;标签的属性|
|html|&lt;html&gt;标签中的内容|
|head|&lt;head&gt;标签中的内容|
|title|&lt;title&gt;标签中的内容|
|metas|一组&lt;meta&gt;标签|
|styles|层叠样式表定义|
|body_attribs|&lt;body&gt;标签的属性|
|body|&lt;body&gt;标签中的内容|
|navbar|用户定义的导航条|
|content|用户定义的页面内容|
|scripts|文档底部的JavaScript声明|

>如果程序需要向已经有内容的块中添加新内容，必须使用Jinja2提供的super()函数。


>Bootstrap中文文档地址:[http://www.bootcss.com/](http://www.bootcss.com/)


## Flask自定义错误页面

像常规路由一样，Flask允许程序使用基于模板的自定义错误页面。最常见的错误代码有两个：404，客户端请求未知页面或路由时显示；500，有未处理的异常时显示。为这两个错误代码指定自定义处理程序的方式如下所示。

```
#404页面
@app.errorhandler(404)
def page_not_found(e):    
	return render_template('404.html'), 404

#500页面
@app.errorhandler(500)
def internal_server_error(e):    
	return render_template('500.html'), 500
```

## Flask设置链接

`url_for()`函数最简单的用法是以视图函数名（或者`app.add_url_route()`定义路由时使用的端点名）作为参数，返回对应的URL。当调用`url_for('index')`得到的结果是/。调用`url_for('index', _external=True)`返回的则是绝对地址`http://local-host:5000/`。

使用`url_for()`生成动态地址时，将动态部分作为关键字参数传入。例如，`url_for('user',name='john', _external=True)`的返回结果是`http://localhost:5000/user/john`。

调用静态文件：`url_for('static', file-name='css/styles.css', _external=True)`得到的结果是`http://localhost:5000/static/css/styles.css`。

> 静态文件需要先在根目录下新建static文件夹


```
# HTML中可以这样写
<a href="{{url_for('static',filename='style.css')}}">test</a>
```


## 使用Flask-Moment本地化日期和时间
有一个使用JavaScript开发的优秀客户端开源代码库，名为`moment.js`，它可以在浏览器中渲染日期和时间。`Flask-Moment`是一个Flask程序扩展，能把`moment.js`集成到Jinja2模板中。

`Flask-Moment`可以使用pip安装

```
pip install flask-moment
```

使用：

flask文件
```
from datetime import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

# 引用Flask-Moment模块
from flask_moment import Moment

app = Flask(__name__)

bootstrap = Bootstrap(app)

#初始化
moment = Moment(app)

@app.route('/')
def index():
    return render_template('index.html',
                           current_time=datetime.utcnow())
```

HTML页面
```
# 在页面中加入下面内容，引入moment.js
{% block script %}
    {{ moment.include_moment() }}　 
    {{ moment.lang('zh-cn') }}
{% endblock %}

#在页面内容显示时间
{% block content%}
<p>The local date and time is {{ moment(current_time).format('LLL') }}.</p>
<p>That was {{ moment(current_time).fromNow(refresh=True) }}.</p>
{% endblock%}
```

>`format('LLL')`根据客户端电脑中的时区和区域设置渲染日期和时间。参数决定了渲染的方式，'L'到'LLLL'分别对应不同的复杂度。`format()`函数还可接受自定义的格式说明符。

>`fromNow()`渲染相对时间戳，而且会随着时间的推移自动刷新显示的时间。这个时间戳最开始显示为“a few seconds ago”，但指定re-fresh参数后，其内容会随着时间的推移而更新。

>`Flask-Moment`实现了moment.js中的`format()`、`fromNow()`、`fromTime()`、`calendar()`、`valueOf()`和`unix()`方法。

> `moment.lang('zh-cn')`渲染的时间戳可实现多种语言的本地化。
> 
> moment.js文档地址：[http://momentjs.com/docs/#/displaying/](http://momentjs.com/docs/#/displaying/)

## Flask Web表单

`Flask-WTF`扩展可以把处理Web表单的过程变成一种愉悦的体验。

Flask-WTF及其依赖可使用pip安装：
```
pip install flask-wtf
```

### CSRF(跨站请求伪造保护)

为了实现CSRF保护，Flask-WTF需要程序设置一个密钥。Flask-WTF使用这个密钥生成加密令牌，再用令牌验证请求中表单数据的真伪。

```
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
```

`app.config`字典可用来存储框架、扩展和程序本身的配置变量。使用标准的字典句法就能把配置值添加到`app.config`对象中。

`SECRET_KEY`配置变量是通用密钥，可在Flask和多个第三方扩展中使用。


### 表单

Python文件
```
from datetime import datetime
from flask import Flask,render_template,url_for
from flask_moment import Moment
from flask_bootstrap import Bootstrap

# 引入表单相关的模块
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import Required

app = Flask(__name__)
# 设置通用密钥
app.config['SECRET_KEY'] = 'HELLO WORLD'
moment = Moment(app)
bootstrap = Bootstrap(app)

# 定义表单类
class loginform(FlaskForm):
    user = StringField('用户名',validators=[Required()])
    password = PasswordField('密码',validators=[Required()])
    submit = SubmitField('登录')

# 把表单类传递到HTML页面
@app.route('/',methods=['GET', 'POST'])
def index():
    user = None
    form = loginform()
	#validate_on_submit 判断是否有post请求
    if form.validate_on_submit():
        user = form.user.data
        form.user.data = ''
    return render_template('index.html',user=user,form = form)

```

把表单渲染成HTML

```
<form method="port">
	 {{form.hidden_tag()}}
    <div>{{form.user.label}}</div>
    <div>{{form.user()}}</div>
    <div>{{form.password.label}}</div>
    <div>{{form.password()}}</div> 
    <!-- 如果要指定id或者class属性可以这样写。   -->
    <div>{{form.submit(id='submit')}}</div>  
</form>
```

使用Flask-Bootstrap，上述表单可使用下面的方式渲染：

```
{% import "bootstrap/wtf.html" as wtf %}
{{ wtf.quick_form(form) }}
```
import指令的使用方法和普通Python代码一样，允许导入模板中的元素并用在多个模板中。导入的`bootstrap/wtf.html`文件中定义了一个使用Bootstrap渲染Falsk-WTF表单对象的辅助函数。

`wtf.quick_form()`函数的参数为Flask-WTF表单对象，使用Bootstrap的默认样式渲染传入的表单。


WTForms支持的HTML标准字段

|字段对象|说明|
|-------|----|
|StringField|文本字段|
|TextAreaField|多行文本字段|
|PasswordField|密码文本字段|
|HiddenField|隐藏文本字段|
|DateField|文本字段,值为 datetime.date 格式|
|DateTimeField|文本字段,值为 datetime.datetime 格式|
|IntegerField|文本字段,值为整数|
|DecimalField|文本字段,值为 decimal.Decimal|
|FloatField|文本字段,值为浮点数|
|BooleanField|复选框,值为 True 和 False|
|RadioField|一组单选框|
|SelectField|下拉列表|
|SelectMultipleField|下拉列表,可选择多个值|
|FileField|文件上传字段|
|SubmitField|表单提交按钮|
|FormField|把表单作为字段嵌入另一个表单|
|FieldList|一组指定类型的字段|


WTForms验证函数

|验证函数|说 明|
|-------|-----|
|Email|验证电子邮件地址|
|EqualTo|比较两个字段的值;常用于要求输入两次密码进行确认的情况|
|IPAddress|验证 IPv4 网络地址|
|Length|验证输入字符串的长度|
|NumberRange|验证输入的值在数字范围内|
|Optional|无输入值时跳过其他验证函数|
|Required|确保字段中有数据|
|Regexp|使用正则表达式验证输入值|
|URL|验证 URL|
|AnyOf|确保输入值在可选值列表中|
|NoneOf|确保输入值不在可选值列表中|



## Flask 重定向和用户会话

用上面的方法生成的页面在浏览器刷新会弹出警告，要求重新提交数据，避免这种情况可以通过重定向post请求。

使用重定向作为POST请求的响应，而不是使用常规响应。重定向是一种特殊的响应，响应内容是URL，而不是包含HTML代码的字符串。浏览器收到这种响应时，会向重定向的URL发起GET请求，显示页面的内容。这个技巧称为Post/重定向/Get模式。

但是用这种方法重定向之后，post请求的数据数据也会丢失，这是就要通过`session`把数据记录下来，用法和Python字典一样。

```
from flask import Flask,render_template,url_for,session,redirect

#......

@app.route('/',methods=['GET', 'POST'])
def index():
    form = loginform()
    if form.validate_on_submit():
        session['user'] = form.user.data
        return redirect(url_for('index'))
        form.user.data = ''
    return render_template('index.html',user=session.get('user'),form = form,current_time=datetime.now())
```

重定向URL用`redirect()`,为了保证URL和定义的路由兼容且保证修改路由名字路径依然可用，所以通过`url_for()`生成URL地址，然后通过`redirect()`进行重定向。

>url_for()中唯一必须指定的参数是端点名，即路由内部名字，默认情况下即是视图函数。

>session.get('name')直接从会话中读取name参数的值。和普通的字典一样，使用get()获取字典中键对应的值以避免未找到键的异常情况，因为对于不存在的键，get()会返回默认值None。


## Flask 设置Flash消息

请求完成后，有时需要让用户知道状态发生了变化。这里可以使用确认消息、警告或者错误提醒，`flash()`函数可实现这种效果。

```
@app.route('/',methods=['GET', 'POST'])
def index():
    form = testform()
    if form.validate_on_submit():
        # 把session的值赋值到user，判断user是否为空或者是否不等于form中的内容，然后生成flash消息
        user = session.get('user')
        if user is not None and user != form.user.data:
            flash('hello')
        session['user'] = form.user.data
        return redirect(url_for('index'))
    return render_template('index.html',user=session.get('user'),form = form)
```


Flask把`get_flashed_messages()`函数开放给模板，用来获取并渲染消息。

```
{% for msg in get_flashed_messages() %}
    {{msg}}
{% endfor %}
```

使用循环是因为在之前的请求循环中每次调用`flash()`函数时都会生成一个消息，所以可能有多个消息在排队等待显示。`get_flashed_messages()`函数获取的消息在下次调用时不会再次返回，因此Flash消息只显示一次，然后就消失了。
 


## 使用Flask-SQLAlchemy管理数据库

Flask-SQLAlchemy是一个Flask扩展，简化了在Flask程序中使用SQLAlchemy的操作。

### 安装
```
pip install flask-sqlalchemy
```

在Flask-SQLAlchemy中，数据库使用URL指定。

MySQL连接：
`mysql://username:password@hostname/database`

python3.x要加上pymysql：
`mysql+pymysql://username:password@hostname/database`

>Flask-SQLAlchemy文档：[http://docs.jinkan.org/docs/flask-sqlalchemy/quickstart.html](http://docs.jinkan.org/docs/flask-sqlalchemy/quickstart.html)

### 使用

在Flask上面使用：
```
from flask_sqlalchemy import SQLAlchemy

# 保存数据库URL到配置中
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root123@192.168.43.140:3306/flasktest'
# 设置每次请求完自动提交
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
#防止出现这个错误 SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and ，SQLALCHEMY_TRACK_MODIFICATIONS默认不能为空，设置成True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# 生成实例
db = SQLAlchemy(app)

# 定义模型，即数据库中的表
class User(db.Model):
    # __tablename__ 用来定义表名，如果没有定义__tablename__ ，Flask-SQLAlchemy会使用一个默认名
    __tablename__ = 'users'
    # db.Column定义该模型的属性，即表中的字段
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(255))
    # __repr__方法用于返回一个可读性的字段表示模型，用于调试可测试时使用
    def __repr__(self):
        return '<User %r>' % self.username

```

>建立模型时要定义表名`__tablename__`，通过`db.Column`设置字段，设置`__repr__`方法用于返回一个可读性的字段表示模型，用于调试可测试时使用

>`db.Column`类构造函数的第一个参数是数据库列和模型属性的类型，其余的参数指定属性的配置选项。

>`Flask-SQLAlchemy`要求每个模型都要定义主键，这一列经常命名为id。

#### 最常用的SQLAlchemy列类型

|类型名|Python类型|说明|
|-----|----------|----|
|Integer|int|普通整数，一般是32位|
|SmallInteger|int|取值范围|
|BigInteger|int或long|不限制精度的整数|
|Float|float|浮点数|
|Numeric|decimal.Decimal|定点数|
|String|str|变长字符串|
|Text|str|变长字符串，对较长或不限长度的字符串做了优化|
|Unicode|unicode|变长Unicode字符串|
|UnicodeText|unicode|变长Unicode字符串，对较长或不限长度的字符串做了优化|
|Boolean|bool|布尔值|
|Date|datetime.date|日期|
|Time|datetime.time|时间|
|DateTime|datetime.datetime|日期和时间|
|Interval|datetime.timedelta|时间间隔|
|Enum|str|一组字符串|
|PickleType|任何Python对象|自动使用Pickle序列号|
|LargeBinary|str|二进制文件|


#### 最常使用的SQLAlchemy列选项

|选项名|说明|
|------|---|
|primary_key|如果设为True，这列就是表的主键|
|unique|如果设为True，这列不允许出现重复的值|
|index|如果设为True，这列创建索引，提升查询效率|
|nullable|如果设为True，这列允许使用空值；如果设为False，这列不允许使用空值|
|default|为这列定义默认值|



### 在Flask-SQLAlchemy中定义关系

一对多数据模型(数据库表设置)
```
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
	#db.relationship与User建立反向关系,backref='role'的值为自定义
    users = db.relationship('User', backref='role')
    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
	#db.ForeignKey设置外键
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
```

`db.ForeignKey`用来设置外键那个表的那个字段，如上面所示的就是User中的role_id外键roles表中的id，就是role_id中的数据必须在roles表中id有这个值，不然出错。

`db.Relationship()`第一个参数表明这个关系的另一端是哪个模型（类）。如果模型类尚未定义，可使用字符串形式指定。第二个参数`backref`，将向User类中添加一个role属性，从而定义反向关系。这一属性可替代role_id访问Role模型，此时获取的是模型对象，而不是外键的值。

```
users = db.relationship('User', backref='role')

#这句代码简单来说Role可以通过users查询到User中的对应的数据，backref设置个反向关系，role值为自定义值，表示User可以通过role在Role中查询对应的数据。
```

大多数情况下，`db.relationship()`都能自行找到关系中的外键，但有时却无法决定把哪一列作为外键。如果User模型中有两个或以上的列定义为Role模型的外键，SQLAlchemy就不知道该使用哪列。如果无法决定外键，你就要为`db.relationship()`提供额外参数，从而确定所用外键。


#### 常用的SQLAlchemy关系选项

|选项名|说明|
|-----|----|
|backref|在关系的另一个模型中添加反向引用|
|primaryjoin|明确指定两个模型之间使用的联结条件。只在模棱两可的关系中需要指定|
|lazy|指定如何加载相关记录。可选值有select（首次访问时按需加载）、immediate（源对象加载后就加载）、joined（加载记录，但使用联结）、subquery（立即加载，但使用子查询）、noload（永不加载）和dynamic（不加载记录，但提供加载记录的查询）|
|uselist|如果设为False，不适用列表，而使用标量值|
|order_by|指定关系记录的排序方式|
|secondary|指定多对多关系中关系表的名字|
|secondaryjoin|SQLAlchemy无法自行决定时，指定多对多关系中的二级联结条件|


>可以参考网站：
>[flask 模型类中relationship的使用及其参数backref的说明](https://blog.csdn.net/fanlei5458/article/details/80464246)
>[遇到一个问题，请各位给讲解一下SQLAlchemy中的backref？](https://www.zhihu.com/question/38456789)

除了一对多之外，还有几种其他的关系类型。一对一关系可以用前面介绍的一对多关系表示，但调用`db.relationship()`时要把`uselist`设为`False`，把“多”变成“一”。多对一关系也可使用一对多表示，对调两个表即可，或者把外键和`db.relationship()`都放在“多”这一侧。最复杂的关系类型是多对多，需要用到第三张表，这个表称为`关系表`。


### 数据库操作

#### 创建表和删除表

```
创建表
db.create_all()

删除表
db.drop_all()
```

注意，如果已经有这个表在数据库中的，`db.create_all()`是不会重新创建或者更新表的。如果模型有改动要重新应用需要先删除表然后重新创建表,不过这样一来原来的数据也会删除了。

#### 插入

>数据模型按照上面代码的建立

```
#设置值
admin_role = Role(name='admin')
user_role = User(username='john',role=admin_role)

#添加
db.session.add(admin_role)
db.session.add(user_role)

#多条数据的可以
#db.session.add_all([admin_role,user_role])

#最后记得要提交
db.session.commit()
```
模型的构造函数接受的参数是使用关键字参数指定的模型属性初始值。注意，role属性也可使用，虽然它不是真正的数据库列，但却是一对多关系的高级表示。

数据库会话也可回滚。调用`db.session.rollback()`后，添加到数据库会话中的所有对象都会还原到它们在数据库时的状态。

#### 修改和删除

```
修改
admin_role.name = 'administrator'
db.session.add(admin_role)
#最后记得要提交
db.session.commit()

删除
db.session.delete(admin_role)
db.session.commit()
```
>修改和删除前要先查询这条数据，还有最后要提交才可以生效

#### 查询

```
查询全部
User.query.all()
查询某一行
User.query.filter_by(role=user_role).all()
或者
user_role = Role.query.filter_by(name='User').first()
```

常用的SQLAlchemy查询过滤器

|过滤器|说明|
|-----|----|
|filter()|把过滤器添加到原查询上，返回一个新查询|
|filter_by()|把等值过滤器添加到原查询上，返回一个新查询|
|limit()|使用指定的值限制原查询返回的结果数量，返回一个新查询|
|offset()|偏移原查询返回的结果，返回一个新查询|
|order_by()|根据指定条件对原数据结果进行排序，返回一个新查询|
|group_by()|根据指定条件对原数据结果进行分组，返回一个新查询|

最常使用的SQLAlchemy查询执行函数

|方法|说明|
|-----|----|
|all()|以列表形式返回查询所有结果|
|first()|返回查询的第一个结果，如果没有结果，则返回None|
|first_or_404()|返回查询的第一个结果，如果没有结果，则终止请求，返回404错误响应|
|get()|返回指定主键对应的行，如果没有对应的行，则返回None|
|get_or_404()|返回指定主键对应的行，如果没有找到对应的主键，则终止请求，返回404错误响应|
|count()|返回查询结果的数量|
|paginate()|返回一个Paginate对象，它包含指定范围内的结果|


#### 集成Python Shell

每次启动shell会话都要导入数据库实例和模型，这真是份枯燥的工作。为了避免一直重复导入，我们可以做些配置，让Flask-Script的shell命令自动导入特定的对象。

```
from flask_script import Shell,Manager
def make_shell_context():
    return dict(app=app, db=db, User=User,Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
```

这段代码的作用是通过`make_shell_context()`函数注册了程序、数据库实例以及模型，因此这些对象能直接导入shell。这样就不用每次进入shell时要引入数据实例。注意的是，这个要在Flask-Script中使用，程序要导入`Manager`并使用。
```
from flask_script import Manager
manager = Manager(app)
#运行
manager.run()
```
然后运行的时候就是通过`python <name>.py shell`进入shell，然后就可以新建数据库和其他操作。

>`<name>.py`表示Python文件名

### 使用Flask-Migrate实现数据库迁移

有时候需要修改数据库模型，而且修改之后还需要更新数据库时。但是`Flask-SQLAlchemy`是仅当数据库表不存在时，才会根据模型进行创建。因此，更新表的唯一方式就是先删除旧表，不过这样做会丢失数据库中的所有数据。所以更新表的更好方法是使用`数据库迁移框架`。

`Flask-Migrate`扩展是对`数据库迁移框架Alembic`做了轻量级包装，并集成到`Flask-Script`中，所有操作都通过`Flask-Script`命令完成。

安装：
```
pip install flask-migrate
```

创建迁移仓库
```
from flask_migrate import Migrate,MigrateCommand
#.....
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)
```

在维护数据库迁移之前，运行一下`python <name>.py db init`，就会创建migrations文件夹，所有的迁移脚本都是放在这里的。

#### 创建迁移脚本

在Alembic中，数据库迁移用迁移脚本表示。脚本中有两个函数，分别是`upgrade()`和`downgrade()`。

`upgrade()`函数把迁移中的改动应用到数据库中，`downgrade()`函数则将改动删除。Alembic具有添加和删除改动的能力，因此数据库可重设到修改历史的任意一点。

我们可以使用revision命令手动创建Alembic迁移，也可使用migrate命令自动创建。

手动创建的迁移只是一个骨架，`upgrade()`和`downgrade()`函数都是空的，开发者要使用Alembic提供的Operations对象指令实现具体操作。

自动创建的迁移会根据模型定义和数据库当前状态之间的差异生成`upgrade()`和`downgrade()`函数的内容。

>注意的是自动创建不一定总是正确，有时候可能会漏掉一下细节，需要检查

创建命令
```
python <name>.py db migrate -m "message"
```
>`-m`的信息随便写，也可以不写。
>修改完数据模型先运行这条命令，然后在用upgrade更新到数据库。

#### 更新数据库

当检查并修正好迁移脚本之后，就可以用`db upgrade`进行更新

```
python <name>.py db upgrade
```
upgrade命令能把改动应用到数据库中，且不影响其中保存的数据。



## 使用Flask-Mail提供电子邮件支持

#### 安装
```
pip install flask-mail
```

#### 配置

```
import os
from flask_mail import Mail
from flask_mail import Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

def send_mail():
    # Message:邮件消息，sender：发送者邮箱；recipients：接收者邮箱，列表格式；body：内容
    msg = Message(subject='Hello World',sender='test@qq.com',recipients=['test@163.com'])
    #邮件内容可以包含主体以及/或者 HTML:
    msg.body = 'sended by flask-mail'
    msg.html = '<h1>test test test !!!!</h1>'
    # Flask-Mail中的send()函数使用cur-rent_app，因此要在激活的程序上下文中执行。
    with app.app_context():
        mail.send(msg)
```

`subject`为邮件标题。
`sender`为发送方，如果你设置了`MAIL_DEFAULT_SENDER`，就不必再次填写发件人，默认情况下将会使用配置项的发件人。

如果 sender 是一个二元组，它将会被分成姓名和邮件地址:
```
msg = Message("Hello",sender=("Me", "me@example.com"))
```

`recipients`为接收方，以列表的形式存在，可以设置一个或者多个收件人，也可以后续再添加。

```
后续添加recipients：
msg.recipients = ["xxx@qq.com"]
msg.add_recipient("xxxx@qq.com")
```

为了保护邮箱账号信息，把邮箱的账号和密码写入环境变量中。

Linux和Mac os添加环境变量:

```
export MAIL_USERNAME= <mail username>
exprot MAIL_PASSWORD= <mail password> 
```
windows:
```
CMD下这样写，邮箱和密码不需要引号
set MAIL_USERNAME= <mail username>
set MAIL_PASSWORD= <mail password> 

powershell下这样写，邮箱和密码要用引号
$env:MAIL_USERNAME='<mail username>'
$env:MAIL_PASSWORD='<mail password>'
```

>`<mail username>`和`<mail password>`表示你的邮箱账号密码，不需要`<>`

然后通过`os.environ.get()`调用。

#### Flask-Mail SMTP服务器的配置

|配置项|默认值|功能|
|-----|------|----|
|MAIL_SERVER|localhost|邮箱服务器|
|MAIL_PORT|25|端口|
|MAIL_USE_TLS|False|是否使用TLS|
|MAIL_USE_SSL|False|是否使用SSL|
|MAIL_DEBUG|app.debug|是否为DEBUG模式，打印调试消息|
|MAIL_SUPPRESS_SEND|app.testing|设置是否真的发送邮件，True不发送|
|MAIL_USERNAME|None|用户名，填邮箱|
|MAIL_PASSWORD|None|密码，填授权码|
|MAIL_DEFAULT_SENDER|None|默认发送者，填邮箱|
|MAIL_MAX_EMAILS|None|一次连接中的发送邮件的上限|
|MAIL_ASCII_ATTACHMENTS|False|如果 MAIL_ASCII_ATTACHMENTS 设置成 True 的话，文件名将会转换成 ASCII 的。一般用于添加附件。|


#### 异步发送电子邮件

如果要异步的可以通过`Thread`实现，

```
from threading import Thread

#.......

def send_async_email(app,msg):
    # Flask-Mail中的send()函数使用cur-rent_app，因此要在激活的程序上下文中执行。
    with app.app_context():
        mail.send(msg)

def send_mail():
    # Message:邮件消息，sender：发送者邮箱；recipients：接收者邮箱，列表格式；body：内容
    msg = Message(subject='Hello World',sender='757147821@qq.com',recipients=['757147821@qq.com','lifetip@163.com'])
    #邮件内容可以包含主体以及/或者 HTML:
    msg.body = 'sended by flask-mail'
    msg.html = '<h1>test test test !!!!</h1>'
    
    # 异步发送邮件
    thread = Thread(target=send_async_email,args=[app,msg])
    thread.start()
```

>Flask-mail文档:[http://www.pythondoc.com/flask-mail/index.html](http://www.pythondoc.com/flask-mail/index.html)


## 大型程序的结构

参考：[https://blog.csdn.net/xingyunlost/article/details/77155584](https://blog.csdn.net/xingyunlost/article/details/77155584)
