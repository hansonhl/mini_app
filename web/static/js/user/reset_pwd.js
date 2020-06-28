;

var user_reset_pwd_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $("div.user_reset_pwd_wrapper button#save").click(function () {
            var btn_element = $(this);
            if (btn_element.hasClass("disabled")) {
                common_ops.alert("Please wait for server to respond");
                return;
            }

            var old_pwd_element = $("div.user_reset_pwd_wrapper input[name='old_password']");
            var new_pwd_element = $("div.user_reset_pwd_wrapper input[name='new_password']");
            var confirm_pwd_element = $("div.user_reset_pwd_wrapper input[name='confirm_password']");

            var old_pwd = old_pwd_element.val();
            var new_pwd = new_pwd_element.val();
            var confirm_pwd = confirm_pwd_element.val();

            if (old_pwd.length < 1) {
                common_ops.alert("请输入原密码!");
                return;
            }
            if (new_pwd.length < 1) {
                common_ops.alert("请输入新密码!");
                return;
            }
            if (confirm_pwd.length < 1) {
                common_ops.alert("请确认新密码!");
                return;
            }
            if (new_pwd != confirm_pwd) {
                common_ops.alert("您确认的密码不一致，请重新输入！");
                old_pwd_element.val("");
                new_pwd_element.val("");
                confirm_pwd_element.val("");
                return;
            }

            btn_element.addClass("disabled");

            $.ajax({
                url: common_ops.buildUrl("/user/reset_pwd"),
                type: "POST",
                data: {old_pwd: old_pwd, new_pwd: new_pwd},
                dataType: "json",
                success: function (res) {
                    btn_element.removeClass("disabled");
                    old_pwd_element.val("");
                    new_pwd_element.val("");
                    confirm_pwd_element.val("");
                    common_ops.alert(res.msg);
                }
            });
        });
    }
}

$(document).ready(function () {
    user_reset_pwd_ops.init();
});