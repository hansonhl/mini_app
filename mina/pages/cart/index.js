//index.js
var app = getApp();
Page({
    data: {},
    onLoad: function () {
    },
    onShow: function () {
        this.getCartList();
    },
    //每项前面的选中框
    selectTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (index !== "" && index != null) {
            list[ parseInt(index) ].active = !list[ parseInt(index) ].active;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        }
    },
    //计算是否全选了
    allSelect: function () {
        var list = this.data.list;
        var allSelect = false;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (curItem.active) {
                allSelect = true;
            } else {
                allSelect = false;
                break;
            }
        }
        return allSelect;
    },
    //计算是否都没有选
    noSelect: function () {
        var list = this.data.list;
        var noSelect = 0;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (!curItem.active) {
                noSelect++;
            }
        }
        if (noSelect == list.length) {
            return true;
        } else {
            return false;
        }
    },
    //全选和全部选按钮
    bindAllSelect: function () {
        var currentAllSelect = this.data.allSelect;
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            list[i].active = !currentAllSelect;
        }
        this.setPageData(this.getSaveHide(), this.totalPrice(), !currentAllSelect, this.noSelect(), list);
    },
    //加数量
    addBtnTap: function (e) {
        var that = this;
        var index = parseInt(e.currentTarget.dataset.index);
        var list = that.data.list;
        list[index].quantity++;
        that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), list);
        this.setCart(list[index].food_id, list[index].quantity);
    },
    //减数量
    minusBtnTap: function (e) {
        var index = parseInt(e.currentTarget.dataset.index);
        var list = this.data.list;
        if (list[index].quantity > 1) {
            list[index].quantity--;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
            this.setCart(list[index].food_id, list[index].quantity);
        }
    },
    //编辑默认全不选
    editTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = false;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    //选中完成默认全选
    saveTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = true;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    getSaveHide: function () {
        return this.data.saveHidden;
    },
    totalPrice: function () {
        var list = this.data.list;
        var totalPrice = 0.00;
        for (var i = 0; i < list.length; i++) {
            if ( !list[i].active) {
                continue;
            }
            totalPrice = totalPrice + parseFloat( list[i].price ) * list[i].quantity;
        }
        return totalPrice;
    },
    setPageData: function (saveHidden, total, allSelect, noSelect, list) {
        this.setData({
            list: list,
            saveHidden: saveHidden,
            totalPrice: total,
            allSelect: allSelect,
            noSelect: noSelect,
        });
    },
    //去结算
    toPayOrder: function () {
        var that = this;
        var purchaseList = [];
        var cartList = this.data.list;
        for (var i = 0; i < cartList.length; i++) {
            if (cartList[i].active) {
                purchaseList.push({
                    "food_id": cartList[i].food_id,
                    "price": cartList[i].price,
                    "quantity": cartList[i].quantity
                });
            }
        }
        var data = {
            type: "cart",
            purchaseList: purchaseList
        };
        wx.navigateTo({
            url: "/pages/order/index?data=" + JSON.stringify(data)
        });
    },
    //如果没有显示去光光按钮事件
    toIndexPage: function () {
        wx.switchTab({
            url: "/pages/food/index"
        });
    },
    //选中删除的数据
    deleteSelected: function () {
        var list = this.data.list;
        var deleted_food_ids = [];
        list = list.filter(function ( item ) {
            if (item.active) {
                deleted_food_ids.push(item.food_id);
            }
            return !item.active;
        });
        this.setPageData( this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        //发送请求到后台删除数据
        wx.request({
            url: app.buildUrl('/cart/delete'),
            method: 'POST',
            data: {deleted: JSON.stringify(deleted_food_ids)},
            header: app.getRequestHeader(),
            success: function (res) {
                // console.log("successfully deleted " + deleted_food_ids.length + "items");
            }
        });
    },
    getCartList: function () {
        var that = this
        wx.request({
            url: app.buildUrl('/cart/index'),
            method: 'GET',
            header: app.getRequestHeader(),
            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({content: res.msg, processing: false});
                    return;
                } else {
                    var data = res.data.data;
                    that.setData({
                        list: data.list,
                        saveHidden: true,
                        allSelect: true,
                        noSelect: false
                    });
                    // console.log("list length " + that.data.list.length);
                    var totalPrice = that.totalPrice();
                    // console.log("totalPrice " + totalPrice);
                    that.setData({totalPrice: totalPrice});
                    // that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(),
                    //     that.noSelect(), that.data.list);
                }
            }
        });
    },
    setCart: function(food_id, quantity) {
        wx.request({
            url: app.buildUrl('/cart/set'),
            method: 'POST',
            data: {food_id: food_id, quantity: quantity},
            header: app.getRequestHeader(),
            success: function (res) {
                // console.log("successfully updated cart entry for food_id " + food_id);
            }
        });
    }
});
