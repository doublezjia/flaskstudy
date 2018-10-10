#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-10-09 10:24:10
# @Author  : zealous (doublezjia@163.com)
# @Link    : https://github.com/doublezjia
# @Version : $Id\
# @Desc       :

from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, ALL

app = Flask(__name__)

# 设置UploadSet
files = UploadSet('files', ALL)
# 配置保存路径
app.config['UPLOADS_DEFAULT_DEST'] = 'uploads'
# 初始化，files为UploadSet设置的值
configure_uploads(app, files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # 如果提交的为POST且提交的表单中存在有media这个名命名的元素
    if request.method == 'POST' and 'media' in request.files:
        # 保存文件
        filename = files.save(request.files['media'])
        # 读取这个文件的url
        url = files.url(filename)
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
