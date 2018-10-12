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