# 用户认证

## 使用Werkzeug的security实现密码散列


使用`Werkzeug.security`模块中的`generate_password_hash`(注册用户),`check_password_hash`(验证用户) 两个函数能够很方便地实现密码散列值的计算。

- `generate_password_hash(password, method=pbkdf2:sha1, salt_length=8)`：这个函数将原始密码作为输入，以字符串形式输出密码的散列值， 输出的值可保存在用户数据库中。`method`和 `salt_length`的默认值就能满足大多数需求。

- `check_password_hash(hash, password)`：这个函数的参数是从数据库中取回的密码散列值和用户输入的密码。返回值为`True`表明密码正确。


例子

`models.py`代码：
```
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    datetime = db.Column(db.DateTime())
    def __repr__(self):
        return '<User %r>' % self.username


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
```

> @property装饰器用于将一个方法变成属性。
> 
> @password.setter 把password变为一个可以赋值的属性


`views.py`代码
```
from flask import render_template,session,url_for,session,flash,redirect

from . import main
from .forms import Nameform
from ..models import User
from .. import db

import datetime

@main.route('/',methods = ['GET','POST'])
def index():
    form = Nameform()
    if form.validate_on_submit():
        session['user'] = form.user.data
        # 添加到数据库
        user = User.query.filter_by(username=form.user.data).first()
        if user is None:
            user = User(username=form.user.data,password=form.pwd.data,datetime=datetime.datetime.now())
            db.session.add(user)
            db.session.commit()   
            flash('add a user')
        else :
            if user.check_password(form.pwd.data) is True:
                flash('password is right')
            else:
                flash('passowrd is wrong')
        # 重定向到页面,这里要注意要用main.index或者.index
        return redirect(url_for('.index'))
    return render_template('index.html',user=session.get('user'),form = form)
```

## 使用Flask-Login认证用户 

Flask-login是一个Flask扩展，首先需要通过pip安装一下
```
pip install flask-login
```

要想使用`Flask-Login`扩展，程序的`User`模型必须实现几个方法。

|方法|说明|
|----|---|
|is_authenticated()|如果用户已经登录就返回True，否则返回False|
|is_active()|如果允许用户登录就返回True，否则返回False，如果是禁用用户就返回False|
|is_anonymous()|对普通用户返回False|
|get_id()|返回用户唯一标识符，使用Unicode编码字符串|


### 设置用于登录的用户模型

Flask-Login提供了一个`UserMixin`类，包含以上方法的默认实现，且能满足大多数需求。

Flask-Login要求程序实现一个回调函数，使用指定的标识符加载用户。

加载用户的回调函数接收以Unicode字符串形式表示的用户标识符。如果能找到用户，这个函数必须返回用户对象；否则应该返回None。

`app/models.py`代码：
```
from flask_login import UserMixin
from . import login_manager

# 继承多一个类UserMixin
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, index=True)
    datetime = db.Column(db.DateTime())
    def __repr__(self):
        return '<User %r>' % self.username
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

# 添加回调函数，使用指定的标识符加载用户。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

### 初始化LoginManager

`app/__init__.py`初始化LoginManager

```
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
	#........

    login_manager.init_app(app)
	
	#........
```

LoginManager对象的`session_protection`属性可以设为`None`、`basic`或`strong`，以提供不同的安全等级防止用户会话遭篡改。设为`strong`时，Flask-Login会记录客户端IP地址和浏览器的用户代理信息，如果发现异动就登出用户。`login_view`属性设置登录页面的端点。



### 设置登录和注册的表单

`app/auth/form.py`表单代码：

```
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import Required,Email,Length,EqualTo
from wtforms import ValidationError
from ..models import User

# 登录表单
class Loginform(FlaskForm):
    email = StringField('Email',validators=[Required(),Email()])
    pwd = PasswordField('password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login IN')

# 注册表单
class Regform(FlaskForm):
    username = StringField('UserName:',validators=[Required()])
    password = PasswordField('PassWord:',validators=[Required()])
    # 通过EqualTo()实现判断密码是否相同
    repassword = PasswordField('Confrm PassWord:',validators=[Required(),
        EqualTo('password',message='Password must match')])
    # 通过Email()实现判断邮箱合法性
    email = StringField('Email:',validators=[Required(),Length(1,64),Email()])
    submit = SubmitField('Register')

    # 如果表单类中定义了以validate_开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    # 判断email和User是否存在
    def validate_email(self,field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email already registered.')
    def validate_username(self,field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('UserName already in use.')
```

> 判断两次输入密码是否一致可以用WTForms的验证方法`EqualTo`实现
> 
> 判断邮箱合法性可以用WTForms的验证方法`Email`实现
> 
> 如果表单类中定义以`validate_`开头且后面跟着字段名的方法的，可以和常规验证函数一起调用。注意这里的`ValidationError`要先通过WTForms引入

### 登录和注册视图设置

`app/auth/views.py`视图代码：

```
from flask import render_template,redirect,flash,request,url_for,session
from . import auth
from ..models import User
from .forms import Loginform
from .forms import Regform
from app import db
from datetime import datetime

from flask_login import login_required,login_user,logout_user

# 登录页面
@auth.route('/login',methods = ['GET','POST']) 
def login():
    form = Loginform()
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(email = form.email.data).first()
        # 如果用户存在且密码正确就登录
        if user is not None and user.check_password(form.pwd.data):
            # flask-login中的login_user()可以标记用户的登录状态为已登录。
            # login_user有一个remember的布尔型的值
            # 如果为False则关闭浏览器就退出登录，如果为True则记录在cookies中，下次直接登录。
            # 这里通过form.remember_me.data传递该值为True或者False
            login_user(user,form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html',form = form)

# 退出登录
@auth.route('/logout')
# @login_required为保护路由，保证只有认证登录的用户才可以访问
@login_required
def logout():
    # flask-login中的logout_user()用来退出登录，删除并重设用户会话
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# 注册页面视图
@auth.route('/register',methods = ['GET','POST'])
def register():
    form = Regform()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data,
            password=form.password.data,
            datetime=datetime.now())
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)
```

> Flask-login中的`login_user()`可以标记用户的登录状态，实现用户登录，通过布尔值实现用户关闭浏览器再打开是否需要重新登录。
>
> Flask-login中的`logout_user()`用来退出登录，删除并重设用户会话
>
> Flask-login中可以通过装饰器`login_required`保护路由，保证只有认证登录的用户才可以访问某些页面。

> 以上的方法都要先通过flask_login引入

### HTML页面

显示表单内容可以通过`{{ wtf.quick_form(form) }}`实现，前提是使用了flask-bootstrap，并在页面中引入`{% import "bootstrap/wtf.html" as wtf %}`

判读用户是否登录成功可以通过`current_user.is_authenticated`实现，`current_user`由Flask-login定义，可以在视图函数和模板中自动可用，如果登录成功的话这个值就是当前登录的用户，如果没有登录就是个匿名用户。`is_authenticated`返回的值为True则登录成功，如果为False则没有登录。

例子：
```
    <h1>Hello,
    {% if current_user.is_authenticated %}
        {{current_user.username}}
    {% else %}
        World
    {% endif %}!
    </h1>
```

> 如果已经登录则显示`Hello 用户名！`，反之就显示`Hello World!`



## 使用itsdangerous生成确认令牌

`itsdangerous`提供了多种生成令牌的方法。其中，`TimedJSONWebSignatureSerializer`类生成具有过期时间的JSON Web签名（JSON Web Signatures，JWS）。这个类的构造函数接收的参数是一个密钥，在Flask程序中可使用`SECRET_KEY`设置。


`dumps()`方法为指定的数据生成一个加密签名，然后再对数据和签名进行序列化，生成令牌字符串。`expires_in`参数设置令牌的过期时间，单位为秒。


为了解码令牌，序列化对象提供了`loads()`方法，其唯一的参数是令牌字符串。这个方法会检验签名和过期时间，如果通过，返回原始数据。如果提供给`loads()`方法的令牌不正确或过期了，则抛出异常。


把方法写在models的类中

例如 `app/models.py`代码

```
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from flask import current_app

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

    def __repr__(self):
        return '<User %r>' % self.username

    # 生成确认令牌
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


```

`generate_confirmation_token()`方法生成一个令牌，有效期默认为一小时。`confirm()`方法检验令牌，如果检验通过，则把新添加的confirmed属性设为True。除了检验令牌，`confirm()`方法还检查令牌中的id是否和存储在`current_user`中的已登录用户匹配。如此一来，即使恶意用户知道如何生成签名令牌，也无法确认别人的账户。


## 发送邮件

邮件代码 `email.py`：

```
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app,msg):
    # Flask-Mail中的send()函数使用cur-rent_app，因此要在激活的程序上下文中执行。
    with app.app_context():
        mail.send(msg)

def send_mail(to,subject,template,**kargs):
    # 永远不要向信号传递 current_app 作为发送端
    # 使用 current_app._get_current_object() 作为替代。
    # 这样的原因是，current_app 是一个代理，而不是真正的应用对象。
    app = current_app._get_current_object()
    # Message:邮件消息，sender：发送者邮箱；recipients：接收者邮箱，列表格式；body：内容
    msg = Message(subject=subject,sender=app.config['MAIL_SENDER'],recipients=[to])
    #邮件内容可以包含主体以及/或者 HTML
    msg.html = render_template(template+'.html',**kargs)
    # msg.body = render_template()
    
    # 异步发送邮件
    thread = Thread(target=send_async_email,args=[app,msg])
    thread.start()

    return thread
```

然后后面发送邮件只要调用`email.py`中的`send_mail`就可以了

邮件中的`template`内容

```
Dear {{user.username}}
    <pre>
    Congratulations on your successful registration.
    please <a href="{{ url_for('auth.confirm',token=token,_external=True) }}">click here</a> to confirm your account.

    if can not click the link ,please copy this URL to the browser

    {{ url_for('auth.confirm',token=token,_external=True) }}

    </pre>

```

`user`是通过`send_mail`传递过来的。`_external=True`的作用是要获取完整的URL。


## 只允许未认证用户访问特定页面。


每个程序都可以决定用户确认账户之前可以做哪些操作。比如，允许未确认的用户登录，但只显示一个页面，这个页面要求用户在获取权限之前先确认账户。

这种情况就可以通过before_request和before_app_request修饰器可以实现。

代码：

```
# 判断是否为认证用户，防止没有认证的用户访问其他页面
# 只有认证了的用户才可以正常访问页面，没有认证的只可以访问特定页面
# 通过before_request和before_app_request修饰器可以实现该功能
# before_request ：只能应用到属于蓝本的请求上
# before_app_request ： 在蓝本中使用针对程序全局的请求
@auth.before_app_request
def before_request():
    # 如果用户登录 且没有认证 且不是访问auth蓝图下的页面和不是访问静态文件就跳转到unconfirmed页面进行认证
    # before_app_request满足一下条件就会被拦截：
    # 1. 用户已登录
    # 2. 没有认证的用户
    # 3.请求的端点不在认证认证蓝本中
    # 4.不是访问静态文件
    if current_user.is_authenticated \
    and not current_user.confirmed \
    and request.blueprint != 'auth' \
    and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))
```


