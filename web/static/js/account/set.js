;

var account_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $("div.account_set_wrapper button.save").click(function () {
            var btn_element = $(this);
            if (btn_element.hasClass("disabled")) {
                common_ops.alert("Please wait for server to respond");
                return;
            }

            var nickname = $("div.account_set_wrapper input[name='nickname']").val();
            var mobile = $("div.account_set_wrapper input[name='mobile']").val();
            var email = $("div.account_set_wrapper input[name='email']").val();
            var login_name = $("div.account_set_wrapper input[name='login_name']").val();
            var login_pwd = $("div.account_set_wrapper input[name='login_pwd']").val();
            var confirm_pwd = $("div.account_set_wrapper input[name='confirm_pwd']").val();

            var uid = $("div.account_set_wrapper input[name='uid']").val();

            if (nickname.length < 1) {
                common_ops.alert("请输入您的姓名!");
                return;
            } else if (mobile.length < 1) {
                common_ops.alert("请输入您的手机号码!");
                return;
            } else if (email.length < 1) {
                common_ops.alert("请输入您的邮箱!");
                return;
            } else if (login_name.length < 1) {
                common_ops.alert("请输入您的用户名!");
                return;
            } else if (login_pwd.length < 6) {
                common_ops.alert("您的登录密码不能短于6个字符!");
                return;
            }

            if (login_pwd != confirm_pwd) {
                common_ops.alert("您输入的两次密码不一致!");
                return;
            }

            btn_element.addClass("disabled");
            console.log("sending ajax")

            $.ajax({
                url: common_ops.buildUrl("/account/set"),
                type: "POST",
                data: {
                    uid: uid,
                    nickname: nickname,
                    mobile: mobile,
                    email: email,
                    login_name: login_name,
                    login_pwd: login_pwd
                },
                dataType: "json",
                success: function (res) {
                    btn_element.removeClass("disabled");
                    var callback_fxn = null;
                    if (res.code == 200) {
                        callback_fxn = function () {
                            window.location.href = common_ops.buildUrl("/account/index")
                        }
                    }
                    common_ops.alert(res.msg, callback_fxn);
                }
            })
        });
    }
}

$(document).ready(function () {
    account_set_ops.init();
});