//获取应用实例
var app = getApp();
Page({
    data: {user_info: null},
    onLoad() {

    },
    onShow() {
        this.getMemberInfo();
    },
    getMemberInfo() {
        var that = this;
        wx.request({
            url: app.buildUrl('/my/index'),
            method: 'GET',
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                } else {
                    var data = res.data.data;
                    that.setData({user_info: data.user_info});
                }
            }
        });
    }
});