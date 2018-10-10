## Flask-uploads文档

> 官方文档：[https://pythonhosted.org/Flask-Uploads/](https://pythonhosted.org/Flask-Uploads/)

> 知乎Hello, Flask!专栏 [https://zhuanlan.zhihu.com/p/24884238](https://zhuanlan.zhihu.com/p/24884238)


## 安装

```
pip install flask-uploads
```

## 使用

Flask-uploads支持'txt', 'rtf', 'odf', 'ods', 'gnumeric', 'abw', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'csv', 'ini', 'json', 'plist', 'xml', 'yaml', 'yml'这些格式的上传，并且归类成TEXT + DOCUMENTS + IMAGES三个集合中。


### 配置

UPLOADED_FILES_DEST：文件保存的目录

UPLOADED_FILES_URL ：如果有服务器保存文件的，这里就写这个服务器URL路径

UPLOADED_FILES_ALLOW ： 设置允许上传的文件

UPLOADED_FILES_DENY ：设置禁止上传的文件

UPLOADS_DEFAULT_DEST ： 设置默认保存目录，如果设置了这个，当上传文件时，会在这个默认目录中新建个子目录存放对应的文件。

UPLOADS_DEFAULT_URL ： 用法和上面类似，如果有服务器存放文件的，设置默认URL

> 上面的FILES是上传文件的配置，如果要上传图片、文档的请把FILES改为PHOTOS或者ATTACHMENTS。



如果是在Flask项目结构中的，直接在配置文件中写上需要的配置，如：

```
UPLOADED_FILES_DEST = 'Uploads'
```

如果是在普通Flask中的，则直接写

```
app.config['UPLOADED_FILES_DEST'] = 'Uploads'
```



设置UploadSet

```
files = UploadSet('files', ALL)
```

> 这里的ALL表示可以上传全部，其他的选择还有TEXT、DOCUMENTS 、IMAGES

初始化

```
configure_uploads(app, files)
```

> 注意这里的files是上面UploadSet设置的值


Flask路由设置

```
# 引入flask中的request，用来判断提交的是否为POST
# 这里的files为UploadSet中设置的值
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'media' in request.files:
        filename = files.save(request.files['media'])
        url = files.url(filename)
    return render_template('upload.html')
```

新建一个HTML，添加表单如下

```
<form action="{{url_for('upload')}}" method="POST" enctype="multipart/form-data">
    <input type="file" id="media" name="media">
    <input type="submit">
</form>
```

method设置为POST,enctype设置为multipart/form-data


Flask文件完整代码

```
from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, ALL

app = Flask(__name__)

files = UploadSet('files', ALL)
app.config['UPLOADS_DEFAULT_DEST'] = 'uploads'
configure_uploads(app, files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'media' in request.files:
        filename = files.save(request.files['media'])
        url = files.url(filename)
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
```


更多Flask-Uploads使用方法可以参考前面的两个网站。