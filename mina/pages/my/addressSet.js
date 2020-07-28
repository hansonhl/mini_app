//获取应用实例
var commonCityData = require('../../utils/city.js');
var app = getApp();
Page({
    data: {
        id: 0,
        provinces: [],
        citys: [],
        districts: [],
        selProvince: '请选择',
        selCity: '请选择',
        selDistrict: '请选择',
        selProvinceIndex: 0,
        selCityIndex: 0,
        selDistrictIndex: 0,
        address: ''
    },
    onLoad: function (e) {
        this.initCityData(1);
        if (e.hasOwnProperty("id")) {
            this.setData({id: e.id});
        }
    },
    onShow: function () {
        if (this.data.id) {
            this.getAddrInfo();
        }
    },
    //初始化城市数据
    initCityData: function (level, obj) {
        if (level == 1) {
            var pinkArray = [];
            for (var i = 0; i < commonCityData.cityData.length; i++) {
                pinkArray.push(commonCityData.cityData[i].name);
            }
            this.setData({
                provinces: pinkArray
            });
        } else if (level == 2) {
            var pinkArray = [];
            var dataArray = obj.cityList
            for (var i = 0; i < dataArray.length; i++) {
                pinkArray.push(dataArray[i].name);
            }
            this.setData({
                citys: pinkArray
            });
        } else if (level == 3) {
            var pinkArray = [];
            var dataArray = obj.districtList
            for (var i = 0; i < dataArray.length; i++) {
                pinkArray.push(dataArray[i].name);
            }
            this.setData({
                districts: pinkArray
            });
        }
    },
    bindPickerProvinceChange: function (event) {
        var selIterm = commonCityData.cityData[event.detail.value];
        this.setData({
            selProvince: selIterm.name,
            selProvinceIndex: event.detail.value,
            selCity: '请选择',
            selCityIndex: 0,
            selDistrict: '请选择',
            selDistrictIndex: 0
        });
        this.initCityData(2, selIterm);
    },
    bindPickerCityChange: function (event) {
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[event.detail.value];
        this.setData({
            selCity: selIterm.name,
            selCityIndex: event.detail.value,
            selDistrict: '请选择',
            selDistrictIndex: 0
        });
        this.initCityData(3, selIterm);
    },
    bindPickerChange: function (event) {
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].districtList[event.detail.value];
        if (selIterm && selIterm.name && event.detail.value) {
            this.setData({
                selDistrict: selIterm.name,
                selDistrictIndex: event.detail.value
            })
        }
    },
    bindCancel: function () {
        wx.navigateBack({});
    },
    bindSave: function (e) {
        var that = this;
        var contactName = e.detail.value.contactName;
        var address = e.detail.value.address;
        var mobile = e.detail.value.mobile;

        if (contactName == "") {
            app.tip({content: "请填写联系人姓名"});
            return;
        }
        if (mobile == "") {
            app.tip({content: "请填写联系人电话号码"});
            return;
        }

        if (this.data.selProvince == "请选择") {
            app.tip({content: "请选择省市地区"});
            return;
        }

        if (this.data.selProvince == "请选择") {
            app.tip({content: "请选择城市"});
            return;
        }
        var provinceId = commonCityData.cityData[this.data.selProvinceIndex].id;
        var cityId = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].id;
        var districtId;

        if (this.data.selDistrict == "请选择" || !that.data.SelDistrict) {
            districtId = 0;
        } else {
            districtId = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].districtList[this.data.selDistrictIndex].id;
        }

        if (address == "") {
            app.tip({content: "请填写详细地址"});
            return;
        }

        var data = {
            id: this.data.id,
            province_id: provinceId,
            province_str: this.data.selProvince,
            city_id: cityId,
            city_str: this.data.selCity,
            district_id: districtId,
            district_str: this.data.selDistrict,
            address: address,
            mobile: mobile,
            contact_name: contactName
        };

        wx.request({
            url: app.buildUrl('/my/address/set'),
            method: 'POST',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                } else {
                    var data = res.data.data;
                    wx.navigateBack();
                }
            }
        });
    },
    getAddrInfo: function() {
        var that = this;
        var data = {id: this.data.id};
        wx.request({
            url: app.buildUrl('/my/address/get'),
            method: 'GET',
            data: data,
            header: app.getRequestHeader(),

            success: function (res) {
                if (res.data.code != 200) {
                    app.alert({"content": res.data.msg});
                } else {
                    var data = res.data.data;
                    that.setData({
                        contactName: data.contact_name,
                        mobile: data.mobile,
                        selProvince: data.province_name,
                        selProvinceIndex: data.province_idx,
                        selCity: data.city_name,
                        selCityIndex: data.city_idx,
                        selDistrict: data.district_name,
                        selDistrictIndex: data.distr_idx,
                        address: data.address
                    });
                }
            }
        });
    },
    deleteAddress: function (e) {

    },
});
