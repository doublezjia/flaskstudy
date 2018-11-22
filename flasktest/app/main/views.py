#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-08-01 16:24:50
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id$
# @@Desc   : 网站视图

from flask import render_template,session,url_for,session,flash,redirect,request,Response

from . import main
from .forms import Nameform
from .forms import EditProfileForm
from .forms import EditProfileAdminForm
from ..models import User,Role,Article
from .. import db

from flask_login import login_required
from flask_login import current_user
import datetime

from ..models import Permission
from ..decorators import permission_required
from ..decorators import admin_required

from .. import photos 
from .forms import FileUploadsForm
from .forms import CkeditorForm

import json,hashlib,time,os
# 管理员页面
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For administrators'

# 有moderate权限才可以访问
@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return 'For commit moderators!'

@main.route('/',methods = ['GET','POST'])
def index():
    return render_template('index.html',user=session.get('user'))

# 用户页面
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    # 如果没有这个用户，返回404
    if user is None:
        abort(404)
    return render_template('user.html',user=user)

# 用户信息修改
@main.route('/user/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
   form = EditProfileForm()
   if form.validate_on_submit():
       current_user.about_me = form.about_me.data
       db.session.add(current_user)
       flash('Your profile has been updated.')
       return redirect(url_for('main.user',username=current_user.username))
   form.about_me.data = current_user.about_me
   return  render_template('edit_profile.html',form=form)


@main.route('/admin/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    # get_or_404(id)通过id查找是否有这个用户，有就返回结果，没有就返回404
    user = User.query.get_or_404(id)
    # 传入user值到EditProfileAdminForm，用来判断修改的值跟原来的是否一样
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        # form.role.data的值为Role表对应的ID值
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')

        # 如果是管理员编辑其他人数据的就返回userlist这个页面
        if current_user.is_administrator and user.id != current_user.id:
            return redirect(url_for('main.userlist'))

        return redirect(url_for('main.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    # user.role_id为对应的Role表中的ID
    form.role.data = user.role_id
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)

# 用户列表
@main.route('/admin/userlist/')
@login_required
@admin_required
def userlist():
    # 查询所有数据
    userlist = User.query.order_by(User.id).all()
    return render_template('userlist.html',userlist=userlist)


# 图片上传
@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = FileUploadsForm()
    if form.validate_on_submit():
        if session.get('imgsrc'):
            imgsrc = session.get('imgsrc')
            current_user.imagesrc = imgsrc
            db.session.add(current_user)
            db.session.commit()
            flash('Add image successful.')
            session['imgsrc'] = ''
            return redirect(url_for('main.upload_file'))
    return render_template('uploads.html',form=form)


# 富文本编辑器tinymce测试页面
@main.route('/ckeditortest',methods=['GET','POST'])
@login_required
def ckeditor_test():
    form = CkeditorForm()
    # 判断登录用户是否有写的权限
    # 因为要获取一个真正的用户对象所以要用_get_current_object
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        article = Article(title=form.title.data,content=form.content.data,
            author=current_user._get_current_object())
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('main.article_list'))
    return render_template('ckeditor_test.html',form=form)

# 修改文章
@main.route('/ckeditoredit/<int:id>',methods=['GET','POST'])
@login_required
def ckeditor_edit(id):
    form = CkeditorForm()
    article = Article.query.get_or_404(id)
    # 判断登录用户是否有写的权限和是否提交
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        return redirect(url_for('main.ckeditor_edit',id=id))
    # 表单显示内容
    form.title.data = article.title
    form.content.data = article.content
    return render_template('ckeditor_edit.html',form=form)


# 文章列表显示页面
@main.route('/articlelist/',methods=['GET','POST'])
def article_list():
    # 分页
    # 页数请求从request.args.get获得，默认为第一页，int型
    page = request.args.get('page',1,type=int)
    # 通过paginate对象来获取记录
    # 参数说明：
    # page为页数,从上面的request.args.get获得
    # per_page为每页显示的记录数
    # error_out设置为True时，超出请求页数范围返回的是404错误，设置为False时返回的时候空列表
    pagination = Article.query.order_by(Article.timestamp.desc()).paginate(page,
        per_page=10,error_out=False)
    # 当前页的记录
    posts = pagination.items
    return render_template('article_list.html',posts = posts,
        pagination=pagination)
# 文章显示页面
@main.route('/articleshow/<int:id>')
def article_show(id):
    article = Article.query.get(id)
    if article is None:
        abort(404)
    return render_template('article_show.html',article=article)


# 用来处理富文本上传图片
@main.route('/tinymceupload',methods=['POST','OPTIONS'])
def tinymceUpload():
    # 如果提交的方式为POST就执行
    if request.method == 'POST':
        # 生成文件名
        Fname = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
        # 通过flask-upload来保存文件，这里获取富文本编辑器中方的文件上传的值为request.files['file']
        img  = photos.save(request.files['file'],name=Fname+'.')
        # 因为保存的文件默认为'/static/uploads/'，所以生成如下路径
        imgsrc = '/static/uploads/'+img
        # 因为tinymce需要返回的值为json，所以新建一个key为location的字典
        # 然后转为json格式在再返回
        imgdict = {
        'location':imgsrc
        }
        img_json = json.dumps(imgdict)
        session['imgsrc'] = imgsrc
        return img_json

# 关注
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    # 如果没有这个用户就跳转到首页
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    # 如果已经关注了就跳到用户页
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s' % username)
    return redirect(url_for('main.user',username=username))

# 取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    # 如果没有关注就跳到用户页
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('main.user',username=username))

# 关注人页面
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=10,
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)

# 被关注人页面
@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=10,
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)