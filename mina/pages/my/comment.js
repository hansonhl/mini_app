//获取应用实例
var app = getApp();
Page({
    data: {
        "content":"非常愉快的订餐体验~~",
        "score":10,
        "order_sn":""
    },
    onLoad: function (e) {
        this.setData({order_sn: e.order_sn});
    },
    scoreChange:function( e ){
        this.setData({
            "score":e.detail.value
        });
    },
    doComment:function(e){
        var that = this;
        var content = e.detail.value.content;
        var data = {
            "content": content,
            "score": this.data.score,
            "order_sn": this.data.order_sn
        };
        wx.request({
            url: app.buildUrl("/my/comment/add"),
            header: app.getRequestHeader(),
            method: "POST",
            data: data,
            success: function (res) {
                var data = res.data.data;
                if (res.data.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                } else {
                    wx.navigateTo({
                        url: "/pages/my/commentList"
                    });
                }
                /*
                that.setData({
                   user_info:resp.data.info
                });
                */
            }
        });
    }
});