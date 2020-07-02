;

var member_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $("div.member_set_wrapper button.save").click(function () {
            var btn_element = $(this);
            if (btn_element.hasClass("disabled")) {
                common_ops.alert("Please wait for server to respond");
                return;
            }

            var nickname = $("div.member_set_wrapper input[name='nickname']").val();
            var id = $("div.member_set_wrapper input[name='id']").val();

            if (nickname.length < 1) {
                common_ops.alert("请输入您的姓名!");
                return;
            }

            btn_element.addClass("disabled");

            $.ajax({
                url: common_ops.buildUrl("/member/set"),
                type: "POST",
                data: {
                    id: id,
                    nickname: nickname
                },
                dataType: "json",
                success: function (res) {
                    btn_element.removeClass("disabled");
                    var callback_fxn = null;
                    if (res.code == 200) {
                        callback_fxn = function () {
                            window.location.href = common_ops.buildUrl("/member/index");
                        }
                    }
                    common_ops.alert(res.msg, callback_fxn);
                }
            })
        });
    }
}

$(document).ready(function () {
    member_set_ops.init();
});