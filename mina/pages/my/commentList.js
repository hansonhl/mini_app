var app = getApp();
Page({
    data: {
        list: [
            {
                date: "2018-07-01 22:30:23",
                order_number: "20180701223023001",
                content: "记得周六发货",
            },
            {
                date: "2018-07-01 22:30:23",
                order_number: "20180701223023001",
                content: "记得周六发货",
            }
        ]
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载
        this.getCommentList();
    },
    onShow: function () {
        var that = this;
    },
    getCommentList: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/my/comment/list"),
            header: app.getRequestHeader(),
            method: "GET",
            success: function (res) {
                var data = res.data.data;
                if (res.data.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                } else {
                    that.setData({
                        list: data.list
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
