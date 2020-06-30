;

var account_index_ops = {
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



            btn_element.addClass("disabled");

            $.ajax({
                url: common_ops.buildUrl("/account/set"),
                type: "POST",
                data: {

                },
                dataType: "json",
                success: function (res) {
                    btn_element.removeClass("disabled");
                    var callback_fxn = null;
                    if (res.code == 200) {

                    }
                    common_ops.alert(res.msg, callback_fxn);
                }
            })
        });
    }
}

$(document).ready(function () {
    account_index_ops.init();
});