;
var upload = {
    error: function (msg) {
        common_ops.alert(msg);
    },
    success: function (file_key) {
        console.log("executing success callback function" + file_key);
        // show image that user uploaded beside the upload image button
        if (file_key) {
            var html = '<img src="' + common_ops.buildImgUrl(file_key) + '"/>'
                + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';

            var uploaded_pic_element = $("form.title_pic_upload_wrapper span.uploaded_pic")
            if (uploaded_pic_element.size() > 0) {
                uploaded_pic_element.html(html);
            } else {
                $("form.title_pic_upload_wrapper").append('<span class="uploaded_pic">' + html + "</span>");
            }
            // rebind event to document when a new image is uploaded
            food_set_ops.delete_img();
        }
    }
};


var food_set_ops = {
    init: function () {
        this.eventBind();
        this.initEditor(); // initialize ueditor, which is a text processor-like UI
        this.delete_img();
    },
    eventBind: function () {
        var that = this;
        // initialize select2 plugin
        $("div.food_set_wrapper select[name=cat_id]").select2({
            language: 'zh-CN',
            width: '100%'
        });

        // initialize tagsinput plugin
        $("div.food_set_wrapper input[name=tags]").tagsInput({
            width: 'auto',
            height: 40,
        });

        // setuo title pic upload
        $("div.food_set_wrapper form.title_pic_upload_wrapper input[name=title_pic]").change(function () {
            $("div.food_set_wrapper form.title_pic_upload_wrapper").submit(); // submit form
        });

        // define save and upload behavior, the following code is provided by the instructor
        $(".food_set_wrapper .save").click(function () {
            var btn_element = $(this);
            if (btn_element.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复提交~~");
                return;
            }

            var food_id = $(".food_set_wrapper input[name=id]").val();
            if (food_id.length < 1) {
                food_id = "0";
            }

            var cat_id_target = $(".food_set_wrapper select[name=cat_id]");
            var cat_id = cat_id_target.val();

            var name_target = $(".food_set_wrapper input[name=name]");
            var name = name_target.val();

            var price_target = $(".food_set_wrapper input[name=price]");
            var price = price_target.val();

            var summary = $.trim(that.ue.getContent());

            var stock_target = $(".food_set_wrapper input[name=stock]");
            var stock = stock_target.val();

            var tags_target = $(".food_set_wrapper input[name=tags]");
            var tags = $.trim(tags_target.val());

            if (parseInt(cat_id) < 1) {
                common_ops.tip("请选择分类~~", cat_id_target);
                return;
            }

            if (name.length < 1) {
                common_ops.alert("请输入符合规范的食品名称~~");
                return;
            }

            if (parseFloat(price) <= 0) {
                common_ops.tip("请输入符合规范的售卖价格~~", price_target);
                return;
            }

            if ($(".food_set_wrapper .uploaded_pic").size() < 1) {
                common_ops.alert("请上传封面图~~");
                return;
            }

            if (summary.length < 10) {
                common_ops.tip("请输入描述，并不能少于10个字符~~", price_target);
                return;
            }

            if (parseInt(stock) < 1) {
                common_ops.tip("请输入符合规范的库存量~~", stock_target);
                return;
            }

            if (tags.length < 1) {
                common_ops.alert("请输入标签，便于搜索~~");
                return;
            }

            btn_element.addClass("disabled");

            var data = {
                cat_id: cat_id,
                name: name,
                price: price,
                title_pic: $(".food_set_wrapper .uploaded_pic .del_image").attr("data"),
                summary: summary,
                stock: stock,
                tags: tags,
                id: food_id
            };

            $.ajax({
                url: common_ops.buildUrl("/food/set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_element.removeClass("disabled");
                    var callback = null;
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/food/index");
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            });

        });
    },

    initEditor: function () {
        var that = this;
        var editorConfigs = {
            toolbars: [
                [ 'undo', 'redo', '|',
                    'bold', 'italic', 'underline', 'strikethrough', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall',  '|','rowspacingtop', 'rowspacingbottom', 'lineheight'],
                [ 'customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
                    'directionalityltr', 'directionalityrtl', 'indent', '|',
                    'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
                    'link', 'unlink'],
                [ 'imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
                    'insertimage', 'insertvideo', '|',
                    'horizontal', 'spechars','|','inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols' ]

            ],
            enableAutoSave:true, // autosave configurations
            saveInterval:60000,
            elementPathEnabled:false,
            zIndex:4,
            serverUrl: common_ops.buildUrl( '/upload/ueditor') // backend destination to upload contents
        };
        that.ue = UE.getEditor("editor", editorConfigs); // id is the html element id
    },
    delete_img: function () {
        $("form.title_pic_upload_wrapper .del_image").unbind().click(function () {
            $(this).parent().remove();
        });
    }
}

$(document).ready(function () {
    food_set_ops.init();
});