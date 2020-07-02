;

var food_cat_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $("div.food_cat_set_wrapper button.save").click(function () {
            var btn_element = $(this);
            if (btn_element.hasClass("disabled")) {
                common_ops.alert("Please wait for server to respond");
                return;
            }

            var name = $("div.food_cat_set_wrapper input[name='name']").val();
            var weight = parseInt($("div.food_cat_set_wrapper input[name='weight']").val());
            var id = $("div.food_cat_set_wrapper input[name='id']").val();

            if (name.length < 1) {
                common_ops.alert("食品类别的名称不能为空!");
                return;
            }
            if (!(weight >= 1 && weight <= 4)) {
                common_ops.alert("食品类别的权重必须为整数且在1-4之间!");
                return;
            }

            btn_element.addClass("disabled");

            $.ajax({
                url: common_ops.buildUrl("/food/cat_set"),
                type: "POST",
                data: {
                    id: id,
                    name: name,
                    weight: weight
                },
                dataType: "json",
                success: function (res) {
                    btn_element.removeClass("disabled");
                    var callback_fxn = null;
                    if (res.code == 200) {
                        callback_fxn = function () {
                            window.location.href = common_ops.buildUrl("/food/cat");
                        }
                    }
                    common_ops.alert(res.msg, callback_fxn);
                }
            })
        });
    }
}

$(document).ready(function () {
    food_cat_set_ops.init();
});