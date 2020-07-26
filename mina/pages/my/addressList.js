//获取应用实例
var app = getApp();
Page({
    data: {
        addressList: []
    },
    selectTap: function (e) {
        //从商品详情下单选择地址之后返回
        wx.navigateBack({});
    },
    addessSet: function (e) {
        var url = "/pages/my/addressSet";
        if (e.currentTarget.dataset.hasOwnProperty("id")) {
            url += "?id=" + e.currentTarget.dataset.id;
        }
        wx.navigateTo({
            url: url
        })
    },
    onShow: function () {
        this.getAddressList();
    },
    getAddressList: function () {
        var that = this;
        wx.request({
            url: app.buildUrl('/my/address/list'),
            method: 'GET',
            data: {},
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                } else {
                    var data = res.data.data;
                    that.setData({
                        addressList: data.address_list
                    });
                }
            }
        });
    }
});
