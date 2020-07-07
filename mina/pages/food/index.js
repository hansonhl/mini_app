//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,
        searchInput: '',
        p: 1, // for dividing search results into pages
        processing: false // whether we are waiting server to send over info for new page 
    },
    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });

        that.setData({
            banners: [
                {
                    "id": 1,
                    "pic_url": "/images/food.jpg"
                },
                {
                    "id": 2,
                    "pic_url": "/images/food.jpg"
                },
                {
                    "id": 3,
                    "pic_url": "/images/food.jpg"
                }
            ],
            categories: [
                {id: 0, name: "全部"},
                {id: 1, name: "川菜"},
                {id: 2, name: "东北菜"},
            ],
            activeCategoryId: 0,
			goods: [
			                {
			                    "id": 1,
			                    "name": "小鸡炖蘑菇-1",
			                    "min_price": "15.00",
			                    "price": "15.00",
			                    "pic_url": "/images/food.jpg"
			                },
			                {
			                    "id": 2,
			                    "name": "小鸡炖蘑菇-1",
			                    "min_price": "15.00",
			                    "price": "15.00",
			                    "pic_url": "/images/food.jpg"
			                },
			                {
			                    "id": 3,
			                    "name": "小鸡炖蘑菇-1",
			                    "min_price": "15.00",
			                    "price": "15.00",
			                    "pic_url": "/images/food.jpg"
			                },
			                {
			                    "id": 4,
			                    "name": "小鸡炖蘑菇-1",
			                    "min_price": "15.00",
			                    "price": "15.00",
			                    "pic_url": "/images/food.jpg"
			                }

			 ],
            loadingMoreHidden: false
        });
        this.getBannerAndCat();
    },
    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
	listenerSearchInput:function( e ){
	        this.setData({
	            searchInput: e.detail.value
	        });
	 },
	toSearch:function( e ){
	        this.setData({
	            p:1,
	            goods:[],
	            loadingMoreHidden:true
	        });
	        this.getFoodList();
	},
    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },
    getBannerAndCat: function () {
        var that = this;
        wx.request({
            url: app.buildUrl('/food/index'),
            method: 'GET',
            header: app.getRequestHeader(),
  
            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.msg});
                    return;
                } else {
                    var data = res.data.data;
                    that.setData({
                        banners: data.bannerList,
                        categories: data.catList
                    })
                }
            }
        });
        that.getFoodList();
    },
    // defines event that happens when we click on an item in the category scroll-view
    catClick: function(e) {
        // e.currentTarget: the wxml element that triggered this event
        // e.currentTarget.id: accessing the "id" attribute of the wxml element
        this.setData({activeCategoryId: e.currentTarget.id});

        // make request to backend
        this.getFoodList();
    },
    getFoodList: function () {
        var that = this;
        var cat_id = that.data.activeCategoryId;
        if (cat_id == "") cat_id = "0";
        wx.request({
            url: app.buildUrl('/food/search'),
            method: 'GET',
            header: app.getRequestHeader(),
            data: {
                cat_id: cat_id,
                mix_kw: that.data.searchInput,
                p: that.data.p
            },
            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.msg});
                    return;
                } else {
                    var data = res.data.data;
                    that.setData({goods: data.list, p: that.data.p + 1 });
                }
            }
        });
    },
    onReachBottom: function () {
        var that = this;
        if (that.data.processing) {
            return;
        }

        that.setData({processing: true});
        setTimeout(function () {
            that.getFoodList();
        }, 500);
        app.console("Reached bottom");
    }
});
