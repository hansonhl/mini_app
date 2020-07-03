;

var food_index_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        $("form.search_wrapper button.search").click(function () {
            $("form.search_wrapper").submit();
        });

        $("table a.remove").click(function () {
            // DOM traversal to obtain nickname
            var name = $(this).parent().siblings("td.name").text();
            // attr(): obtain info stored in an html element attribute
            var id = $(this).attr("data");

            // that: use that here because "this" in the scope of the function has changed
            that.ops("remove", {id: id, name: name});
        });
        $("table a.recover").click(function () {
            var name = $(this).parent().siblings("td.name").text();
            var id = $(this).attr("data");
            that.ops("recover", {id: id, name: name});
        });
    },

    // define one function to manage different operations on index.js
    ops: function (act, args) {
        var callback = {
            "ok": function () {
                $.ajax({
                url: common_ops.buildUrl("/food/ops"),
                type: "POST",
                data: {
                    act: act,
                    id: args.id,
                },
                dataType: "json",
                success: function (res) {
                    var callback_fxn = null;
                    if (res.code == 200) {
                        callback_fxn = function () {
                            window.location.reload();
                        }
                    }
                    common_ops.alert(res.msg, callback_fxn);
                }
            })
            },
            "cancel": null
        };
        var confirm_msg = "";
        if (act === "remove") {
            confirm_msg = "确定移除菜品 " + args.name + " ？";
        } else {
            confirm_msg = "确定恢复 " + args.name + " ？";
        }
        common_ops.confirm(confirm_msg, callback)

    }
}

$(document).ready(function () {
    food_index_ops.init();
});