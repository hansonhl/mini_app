;

var user_edit_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $("div.user_edit_wrapper button.save").click(function () {
            var btn_element = $(this);
            if (btn_element.hasClass("disabled")) {
                common_ops.alert("Please wait for server to respond");
                return;
            }

            var nickname = $("div.user_edit_wrapper input[name='nickname']").val();
            var email = $("div.user_edit_wrapper input[name='email']").val();

            if (nickname === undefined && email === undefined || nickname.length < 1 && email.length < 1) {
                common_ops.alert("请输入您的姓名和邮箱!");
            } else if (nickname.length < 1) {
                common_ops.alert("请输入您的姓名!");
                return;
            } else if (email.length < 1) {
                common_ops.alert("请输入您的邮箱!");
                return;
            }

            btn_element.addClass("disabled");

            $.ajax({
                url: common_ops.buildUrl("/user/edit"),
                type: "POST",
                data: {nickname: nickname, email: email},
                dataType: "json",
                success: function (res) {
                    btn_element.removeClass("disabled");
                    $("li.user_info div.dropdown-name").text("姓名：" + nickname);
                    $("li.user_info div.dropdown-email").text("邮箱：" + email);
                    common_ops.alert(res.msg);
                }
            })
        });
    }
}

$(document).ready(function () {
    user_edit_ops.init();
});