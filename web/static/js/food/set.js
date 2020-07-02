;

var food_set_ops = {
    init: function () {
        this.eventBind();
        this.initEditor(); // initialize ueditor, which is a text processor-like UI
    },
    eventBind: function () {

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
    }
}

$(document).ready(function () {
    food_set_ops.init();
});