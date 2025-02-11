//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
var Utils = require("../../utils/util.js");

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax: 1,
        shopCarNum: 0,
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        commentCount:2
    },
    onLoad: function (e) {
        var that = this;
        that.setData({id: e.id}); // e directly contains html GET style arguments
    },
    onShow: function () {
        this.getFoodInfo();
        this.getComments();
    },
    getFoodInfo: function () {
        var that = this;
        wx.request({
            url: app.buildUrl('/food/info?id=' + this.data.id),
            method: 'GET',
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                    return;
                } else {
                    var data = res.data.data;
                    var quantity = data.info.cart_quantity;
                    var buyNumber = app.boundInt(quantity, that.data.buyNumMin, data.info.stock);
                    that.setData({
                        info: data.info,
                        buyNumMax: data.info.stock,
                        buyNumber: buyNumber
                    })
                    WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);
                }
            }
        });

    },
    getComments: function () {
      var that = this;
      wx.request({
            url: app.buildUrl('/food/comment?id=' + this.data.id),
            method: 'GET',
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                    return;
                } else {
                    that.setData({
                        commentList: res.data.data.list,
                        commentCount: res.data.data.list.length
                    })
                }
            }
        });
    },
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },
    addShopCar: function () {
        var that = this;
        var data = {
            food_id: this.data.id,
            quantity: this.data.buyNumber
        };
        wx.request({
            url: app.buildUrl('/cart/set'),
            method: 'POST',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                app.alert({"content": res.data.msg});
                that.setData({hideShopPopup: true, shopCarNum: data.quantity});
            }
        });
    },
    buyNow: function () {
        var purchaseList = [{
            "food_id": this.data.info.id,
            "price": this.data.info.price,
            "quantity": this.data.buyNumber
        }];

        var data = {
            type: "info",
            purchaseList: purchaseList
        };
        this.setData({
            hideShopPopup: true
        });
        wx.navigateTo({
            url: "/pages/order/index?data=" + JSON.stringify(data)
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        })
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if( this.data.buyNumber <= this.data.buyNumMin){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if( this.data.buyNumber >= this.data.buyNumMax ){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    // This is executed when a button with the open-type="share" attribute is clicked
    // or when the "share" option is clicked in the upper-right "..." menu
    onShareAppMessage: function () {
        var that = this;
        return {
            title: that.data.info.name,
            path: app.buildUrl("/food/info?id=" + that.data.info.id),
            /*
            success: function () {
                // share successful, record this sharing instance to backend
                wx.request({
                    url: app.buildUrl('/food/info?id=' + this.data.id),
                    method: 'POST',
                    data: {
                        url: Utils.getCurrentPageUrlWithArgs()
                    },
                    header: app.getRequestHeader(),
                    success: function (res) {
                        
                    }
                });
            },
            fail: function () {
                //转发失败
            }
            */
           // success and fail are no longer supported
        }
    }

});
