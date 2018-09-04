import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from flask_sqlalchemy import SQLAlchemy

from flask_script import Shell,Manager
from flask_migrate import Migrate,MigrateCommand

from flask_mail import Mail
from flask_mail import Message

from threading import Thread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root123@192.168.43.140:3306/flasktest'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False

app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')


bootstrap = Bootstrap(app)
manager = Manager(app)

db = SQLAlchemy(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)

mail = Mail(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    time = db.Column(db.Time)
    def __repr__(self):
        return '<User %r>' % self.username




class testform(FlaskForm):
    user = StringField('name',validators=[Required()])
    submit = SubmitField('submit')


@app.route('/',methods=['GET', 'POST'])
def index():
    form = testform()
    if form.validate_on_submit():
        # 把session的值赋值到user，判断user是否为空或者是否不等于form中的内容，然后生成flash消息
        user = session.get('user')
        if user is not None and user != form.user.data:
            flash('hello')
        session['user'] = form.user.data

        user = User(username=form.user.data)
        db.session.add(user)
        db.session.commit()   


        return redirect(url_for('index'))
    return render_template('index.html',user=session.get('user'),form = form)


def make_shell_context():
    return dict(app=app, db=db, User=User,Role=Role,mail=mail)


def send_async_email(app,msg):
    # Flask-Mail中的send()函数使用cur-rent_app，因此要在激活的程序上下文中执行。
    with app.app_context():
        mail.send(msg)

def send_mail():
    # Message:邮件消息，sender：发送者邮箱；recipients：接收者邮箱，列表格式；body：内容
    msg = Message(subject='Hello World',sender='abc@qq.com',recipients=['abc@qq.com','abc@163.com'])
    #邮件内容可以包含主体以及/或者 HTML:
    msg.body = 'sended by flask-mail'
    msg.html = '<h1>test test test !!!!</h1>'
    
    # 异步发送邮件
    thread = Thread(target=send_async_email,args=[app,msg])
    thread.start()
    




if __name__ == '__main__':
    # send_mail()
    manager.add_command("shell", Shell(make_context=make_shell_context))
    manager.run()



    