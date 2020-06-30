;

var user_login_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $("div.login_wrapper button.do-login").click(function () {
            var btn_element = $(this);
            if (btn_element.hasClass("disabled")) {
                common_ops.alert("Please wait for server to respond");
                return;
            }

            // verify login
            login_name = $("div.login_wrapper input[name='login_name']").val();
            login_pwd = $("div.login_wrapper input[name='login_pwd']").val();
            if ( login_name === undefined || login_name.length < 1) {
                common_ops.alert("Please enter a username!");
                return;
            }

            if (login_pwd === undefined || login_pwd.length < 1) {
                common_ops.alert("Please enter a password!");
                return;
            }

            btn_element.addClass("disabled")

            $.ajax({
                url: common_ops.buildUrl("/user/login"),
                type: "POST",
                data: {
                    login_name: login_name,
                    login_pwd: login_pwd
                },
                dataType: "json",
                success: function(res) {
                    btn_element.removeClass("disabled");
                    var callback_fxn = null;
                    if (res.code == 200) {
                        callback_fxn = function() {
                            window.location.href = common_ops.buildUrl("/");
                        };
                    }
                    common_ops.alert(res.msg, callback_fxn);
                }
            })
        });
    }
}

$(document).ready(function ()  {
    user_login_ops.init();
});