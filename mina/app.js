//app.js
App({
    onLaunch: function () {
    },
    globalData: {
        userInfo: null,
        version: "1.0",
        shopName: "Python3 + Flask 订餐全栈系统",
        domain:"http://192.168.1.171:5000/api"
    },
    tip:function( params ){
        var that = this;
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            success: function(res) {

                if ( res.confirm ) {//点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{//点击否
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    alert:function( params ){
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            showCancel:false,
            success: function(res) {
                if (res.confirm) {//用户点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    console:function( msg ){
        console.log( msg);
    },
    getRequestHeader:function(){
        return {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': this.getCache("token")
        }
    },
    buildUrl: function(path, params) {
        //params = { "test":"abc","sort":"asc" };
        // ?test=abc&sort=asc
        var url = this.globalData.domain + path;
        var _param_url = "";
        if( params ) {
            _param_url = Object.keys(params).map(function (k) {
                return [ encodeURIComponent(k),encodeURIComponent( params[k] ) ].join("=")
            }).join("&");
            _param_url = "?" + _param_url;
        }
        return url + _param_url;
    },
    getCache: function(key) {
        // wechat fxns to manipulate key-value pairs locally
        // getStorageSync() and getStorage() have different syntax!!!!!
        var value = null;
        try {
            value = wx.getStorageSync(key);
        } catch (e) {

        }
        return value;
    },
    setCache: function(key, value) {
        wx.setStorage({
          data: value,
          key: key
        });
    },
    boundInt: function(value, min, max) {
        if (value < min) value = min;
        if (value > max) value = max;
        return value
    }
});