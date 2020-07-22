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
        this.getOrderList();
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
    },
    toPay: function (e) {
        var that = this;
        var template_ids = ["7--0oU7_LN9YjbGFUmRnLDpfikYeC09tpcVnRPffZHY"];
        var data = {
            order_sn: e.currentTarget.dataset.ordersn,
            subscribed: false
        }
        // request user's permission to allow subscribe messages
        wx.requestSubscribeMessage({
            tmplIds: template_ids,
            success: function (res) {
                for (var id of template_ids) {
                    if (res.hasOwnProperty(id) && res[id] == "accept") {
                        data.subscribed = true;
                    }
                }
                that.doPay(data);
            },
            fail: function (res) {
                that.doPay(data);
            }
        })
    },
    doPay: function (data) {
        var that = this;
        wx.request({
            url: app.buildUrl('/order/pay'),
            method: 'POST',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content":res.data.msg});
                } else {
                    var data = res.data.data;
                    var prepay_info = data.prepay_info;
                    if (!data.dev_mode) {
                        that.finishPay(prepay_info);
                    } else {
                        that.finishPayDev(data);
                    }
                }
            }
        });
    },
    finishPay: function (prepay_info) {
        var that = this;
        app.console("Requesting payment, prepay_info" + JSON.stringify(prepay_info));
        wx.requestPayment({
            "timeStamp": prepay_info.timeStamp,
            "nonceStr": prepay_info.nonceStr,
            "package": prepay_info.package,
            "signType": "MD5",
            "paySign": prepay_info.paySign,
            "success": function (res) {
                app.console("success: ", res);
                that.onShow();
            },
            "fail": function (res) {
                app.console("Fail: " + JSON.stringify(res));
                that.onShow();
            }
        });
    },
    finishPayDev: function (data) {
        // directly send callback to backend to complete
        // payment loop for development purposes.
        var that = this;
        var cb_dev_data = {xml: data.cb_dev_data};
        wx.request({
            url: app.buildUrl("/order/callback_dev"),
            method: "POST",
            data: cb_dev_data,
            header: app.getRequestHeader(),
            success: function (res) {
                app.alert({"content":res.data.msg});
                that.onShow();
            }
        });
    }
})
