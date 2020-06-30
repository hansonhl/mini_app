;

var account_index_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        $("form.search_wrapper button.search").click(function () {
            $("form.search_wrapper").submit();
            console.log("sent result");
        });
        $("table a.remove").click(function () {
            //
            var nickname = $(this).parent().siblings("td.nickname").text();

            // attr(): obtain info stored in an html element attribute
            var uid = $(this).attr("data");

            // that: use that here because "this" in the scope of the function has changed
            that.ops("remove", {uid: uid, nickname: nickname});
        });
        $("table a.recover").click(function () {
            var nickname = $(this).parent().siblings("td.nickname").text();
            var uid = $(this).attr("data");
            that.ops("recover", {uid: uid, nickname: nickname});
        });
    },
    ops: function (act, args) {
        var callback = {
            "ok": function () {
                $.ajax({
                url: common_ops.buildUrl("/account/ops"),
                type: "POST",
                data: {
                    act: act,
                    uid: args.uid,
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
        var confirm_msg = ""
        if (act === "remove") {
            confirm_msg = "确定移除 " + args.nickname + " 的账户？";
        } else {
            confirm_msg = "确定恢复 " + args.nickname + " 的账户？";
        }
        common_ops.confirm(confirm_msg, callback)

    }
}

$(document).ready(function () {
    account_index_ops.init();
});