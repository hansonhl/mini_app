//获取应用实例
var app = getApp();
Page({
    data: {
        addressList: []
    },
    selectTap (e) {
        // select an address as default address
        var id = e.currentTarget.dataset.id;
        var action = "set_default";
        var that = this;
        wx.request({
            url: app.buildUrl('/my/address/ops'),
            method: 'POST',
            data: {id: id, action: action},
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                } else {
                    var data = res.data.data;
                    that.getAddressList();
                }
            }
        });
    },
    addessSet (e) {
        var url = "/pages/my/addressSet";
        if (e.currentTarget.dataset.hasOwnProperty("id")) {
            url += "?id=" + e.currentTarget.dataset.id;
        }
        wx.navigateTo({
            url: url
        })
    },
    onShow () {
        this.getAddressList();
    },
    getAddressList () {
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
