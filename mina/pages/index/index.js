//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {}
  },
  goToIndex:function(){
    wx.switchTab({
      url: '/pages/food/index',
    });
  },
  onLoad:function(){
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    })
  },
  onShow:function(){

  },
  onReady: function(){
    var that = this;
    setTimeout(function(){
      that.setData({
        remind: ''
      });
    }, 1000);
    wx.onAccelerometerChange(function(res) {
      var angle = -(res.x*30).toFixed(1);
      if(angle>14){ angle=14; }
      else if(angle<-14){ angle=-14; }
      if(that.data.angle !== angle){
        that.setData({
          angle: angle
        });
      }
    });
  },
  // This login fxn is bound with "button.confirm-btn" in pages/index/index.wxml
  login: function (e) {
    // obtain very basic user info. This info cannot be used to actually login a user
    if (!e.detail.userInfo) {
      // app.alert() is a helper fxn def'd in app.js, provided by imooc instructor
      app.alert({"content":"登录失败，请再试"});
      return;
    }
    var data = e.detail.userInfo;

    wx.login({
      success: function (res) {
        if (!res.code) {
          // app.alert() is a helper fxn def'd in app.js, provided by imooc instructor
          app.alert({"content": "登录失败，请再试"});
          return;
        }
        // obtain login code
        data['login_code'] = res.code;
        // send request to server backend
        // 勾选 设置->项目设置->不校验合法域名..., 以下request才可以使用
        wx.request({
          url: 'http://192.168.1.171:5000/api/member/login',
          method: 'POST',
          data: data,
          // 自定义header, getRequestHeader() is defined in app.js, provided by imooc instructor
          // This allows `data` to be processed as a normal html json form
          header: app.getRequestHeader(),
          success: function (res) {
    
          }
        });
      }
    });

   
    
  }
});