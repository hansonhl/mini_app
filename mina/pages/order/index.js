//获取应用实例
var app = getApp();

Page({
    data: {
        order_list: [],
        default_address: null,
        deliver_price: "0.00",
        pay_price: "0.00",
        total_price: "0.00",
        params: null
    },
    onShow: function () {
        var that = this;
        this.getOrderInfo();
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            params: JSON.parse(e.data)
        });
    },
    createOrder: function (e) {
        wx.showLoading();
        var that = this;
        var data = {
            type: this.data.params.type,
            purchaseList: JSON.stringify(this.data.params.purchaseList)
        };

        wx.request({
            url: app.buildUrl('/order/create'),
            method: 'POST',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                wx.hideLoading();
                if (res.data.code != 200) {
                    app.alert({"content":res.data.msg});
                } else {
                    // use redirectTo() instead of navigateTo() to prevent user from returning
                    // back to this page and submit a duplicate order
                    wx.redirectTo({
                        url: "/pages/my/order_list"
                    });
                }
            }
        });
    },
    addressSet: function () {
        wx.navigateTo({
            url: "/pages/my/addressSet"
        });
    },
    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList"
        });
    },
    getOrderInfo: function () {
        var that = this;
        var data = {
            type: this.data.params.type,
            purchaseList: JSON.stringify(this.data.params.purchaseList)
        };
        wx.request({
            url: app.buildUrl('/order/info'),
            method: 'POST',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content":res.data.msg});
                } else {
                    var data = res.data.data;
                    that.setData({
                        order_list: data.order_list,
                        default_address: data.default_address,
                        deliver_price: data.deliver_price,
                        pay_price: data.pay_price,
                        total_price: data.total_price
                    });
                }
            }
        });
    }
});
