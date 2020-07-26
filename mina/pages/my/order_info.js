var app = getApp();
Page({
    data: {},
    onLoad: function (e) {
        this.setData({order_sn: e.order_sn});
    },
    onShow: function () {
        this.getPayOrderInfo();
    },
    getPayOrderInfo: function () {
        var that=this;
        var data = {
            order_sn: this.data.order_sn
        };
        wx.request({
            url: app.buildUrl('/my/order/info'),
            method: 'GET',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                } else {
                    var data = res.data.data;
                    that.setData({
                        info: data
                    });
                }
            }
        });
    }
});