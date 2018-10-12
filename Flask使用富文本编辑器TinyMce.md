# Flask使用富文本编辑器TinyMce

## 下载tinymce

首先先下载tinymce，这里使用的是版本是4.8.3。

下载tinymce地址：[https://www.tiny.cloud/get-tiny/self-hosted/](https://www.tiny.cloud/get-tiny/self-hosted/)

下载tinymce中文语言包：[https://www.tiny.cloud/get-tiny/language-packages/](https://www.tiny.cloud/get-tiny/language-packages/)



## 前端处理

把下载好的tinymce解压到static目录下，把语言包放在解压出来的tinymce目录下的langs目录里面

然后在tinymce目录下新建一个tinymce_setup.js的文件，并写上以下代码：

```
tinymce.init({
            selector: "textarea",
            height: 400,
            language:'zh_CN',
            plugins: [
                'advlist autolink lists link  charmap print preview hr anchor pagebreak',
                'searchreplace wordcount visualblocks visualchars code fullscreen',
                'insertdatetime media nonbreaking save table contextmenu directionality',
                'emoticons template paste textcolor colorpicker textpattern imagetools codesample toc help image'
              ],
              toolbar1: 'undo redo | insert | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link ',
              toolbar2: 'print preview media | forecolor backcolor emoticons | codesample help image',
              templates: [
                { title: 'Test template 1', content: 'Test 1' },
                { title: 'Test template 2', content: 'Test 2' }
              ],
            menubar: false,

            //TinyMCE 会将所有的 font 元素转换成 span 元素
            convert_fonts_to_spans: true,
            //换行符会被转换成 br 元素
            convert_newlines_to_brs: false,
            //在换行处 TinyMCE 会用 BR 元素而不是插入段落
            force_br_newlines: false,
            //当返回或进入 Mozilla/Firefox 时，这个选项可以打开/关闭段落的建立
            force_p_newlines: false,
            //这个选项控制是否将换行符从输出的 HTML 中去除。选项默认打开，因为许多服务端系统将换行转换成 <br />，因为文本是在无格式的 textarea 中输入的。使用这个选项可以让所有内容在同一行。
            remove_linebreaks: false,
            //不能把这个设置去掉，不然图片路径会出错
            relative_urls: false,
            //不允许拖动大小
            resize: false,

            images_upload_handler: function (blobInfo, success, failure) {
              var xhr, formData;

              xhr = new XMLHttpRequest();
              xhr.withCredentials = false;
              // 通过POST提交数据，/tinymceupload用来后台保存图片并返回json格式的文件地址的路由地址
              xhr.open('POST', '/tinymceupload');
              xhr.onload = function() {
                var json;

                if (xhr.status != 200) {
                  failure('HTTP Error: ' + xhr.status);
                  return;
                }

                json = JSON.parse(xhr.responseText);

                if (!json || typeof json.location != 'string') {
                  failure('Invalid JSON: ' + xhr.responseText);
                  return;
                }
                
                success(json.location);
              };


              formData = new FormData();
              formData.append('file', blobInfo.blob(), blobInfo.filename());
              xhr.send(formData);
            }
        });
```

> 以上代码为tinymce的配置和处理图片上传代码，通过images_upload_handler处理本地上传的图片，配置在tinymce文档中有写。

> images_upload_handler中通过XMLHttpRequest的POST提交把图片上传到`/tinymceupload`路由来处理保存图片并返回路径的json值。

> 注意，这里的`relative_urls: false`要设置为false，不然保存的图片路径不正确。`selector`中的值为`textarea`，控件的名字，也可以设置成对应控件的id。


html中插入js代码

```
<script src="{{ url_for('static',filename='tinymce/tinymce.min.js') }}"></script>

<script src="{{ url_for('static',filename='tinymce/tinymce_setup.js') }}"></script>
```


## 后台处理上传图片

views中添加一个路由用来处理上传的图片

```
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
        return img_json
```

这里是通过flask-uploads进行图片的保存，使用flask-uplaods要先通过pip并进行设置，代码中的photos为flask-uploads设置的值。具体可以参考文档。

> flask-uploads文档：[https://pythonhosted.org/Flask-Uploads/](https://pythonhosted.org/Flask-Uploads/)

这里要返回json到前端，所以要在views中引入json，然后使用。还有这里的request要先通过`from flask import request`引入。

>注意，因为前端的json获取的key为`location`，所以这里的字典写的是`location`，因为前端富文本编辑器中的图片上传控件名为file，所以这里是`request.files['file']`。

这里的保存的文件名是通过时间的md5生成，所以要引入hashlib和time包。

## 页面表单和路由


### 新建一个表单类

```
# 富文本编辑器
class CkeditorForm(FlaskForm):
    content = TextAreaField()
    submit = SubmitField('Submit')
```

这里使用的是TextAreaField

### 编写路由

```
# 富文本编辑器tinymce测试页面
@main.route('/ckeditortest',methods=['GET','POST'])
def ckeditor_test():
    form = CkeditorForm()
    if form.validate_on_submit():
        content = Content(content=form.content.data)
        return redirect(url_for('main.ckeditor_test'))
    return render_template('ckeditor_test.html',form=form)
```

路由这里和正常一样写法，点击提交，获取表单数据。


### HTML页面

HTML页面表单代码如下
```
<form method="POST" action="{{url_for('main.ckeditor_test')}}">
    {{form.hidden_tag()}}
    <div>{{form.content()}}</div>
    <div>{{form.submit()}}</div>
</form>
```

这样就可以使用富文本编辑器了。



tinymce文档：[https://www.tiny.cloud/docs/](https://www.tiny.cloud/docs/)