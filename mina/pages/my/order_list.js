var app = getApp();
Page({
    data: {
        statusType: ["待付款", "待发货", "待收货", "待评价", "已完成","已关闭"],
        status:[ "-8","-7","-6","-5","1","0" ],
        currentStatusIdx: 0,
        tabClass: ["", "", "", "", "", ""]
    },
    statusTap: function (e) {
        var currStatusIdx = e.currentTarget.dataset.index;
        this.data.currentStatusIdx = currStatusIdx;
        this.setData({
            currentStatusIdx: currStatusIdx
        });
        this.onShow();
    },
    orderDetail: function (e) {
        wx.navigateTo({
            url: "/pages/my/order_info"
        })
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载

    },
    onReady: function () {
        // 生命周期函数--监听页面初次渲染完
    },
    onShow: function () {
        var that = this;
        this.getOrderList();
    },
    onHide: function () {
        // 生命周期函数--监听页面隐藏

    },
    onUnload: function () {
        // 生命周期函数--监听页面卸载

    },
    onPullDownRefresh: function () {
        // 页面相关事件处理函数--监听用户下拉动作

    },
    onReachBottom: function () {
        // 页面上拉触底事件的处理函数

    },
    getOrderList: function () {
        var that = this;
        var data = {
            status: parseInt(this.data.status[this.data.currentStatusIdx])
        }
        wx.request({
            url: app.buildUrl('/my/order'),
            method: 'POST',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content":res.data.msg});
                } else {
                    var data = res.data.data;
                    that.setData({
                        order_list: data.pay_order_list
                    });
                }
            }
        });
    }
})
