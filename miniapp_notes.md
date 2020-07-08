# Notes for common operations on WeChat MiniApp frontend

## Basic Structure

### Global configurations

`app.json` and `project.config.json` define basic global configurations of the miniapp.

The first item in the `"pages"` list (which is `pages/index/index` in our case)
is the first page that will be showed when opening the miniapp.

`app.js` defines the `App` object that is visible globally, contains the 
`globalData` field that stores global variables. The `App` object also defines
various helper functions that could be accessed globally, which include:

- `app.alert()` for displaying pop-up window
- `app.console()` for logging
- `app.getRequestHeader()` to allow request data from front end to back end be treated as an html form, 
- `app.buildUrl()` as a general url manager
- `app.getCache()` and `app.setCache()` to store cookie-type data locally in wechat front end

### Structure of each page

Each page has 4 components:

1. `***.wxml` similar to HTML, defines the skeleton structure of page
2. `***.wxss` similar to CSS file, defines appearance of `.wxml` page
3. `***.js` defines a `Page` object, containing functions that are called when events happen to elements 
   in the `.wxml` page. Note that different from jQuery, there is no way to directly change elements in 
   the `.wxml` by js. Instead we need to modify variables in the `data` field, and elements in the `wxml`
   page depend on these variables.
4. `***.json` some config options for the page (not clear yet what this does)


## Basic templating in wxml

### Accessing variables

In wxml, `data` variables are directly accessible by their name enclosed in `{{ }}`.

```xml
<view class="{{myvar2}}">
    {{myvar}}
</view>
```

**NOTE** Avoid spaces between `{{ }}` and the `" "` that enclose it.

**NOTE** `{{true}}` and `{{false}}` are in fact reserved boolean values. Some tag attributes require this
and won't work if the attribute value is the bare string `true` or `false`.

Simple operations can happen within `{{ }}`, similar to Flask templating. These include:

- `? :` statements: `{{flag ? true : false}}`
- Mathematical operations `+ - * /` etc
- Boolean expressions `<view wx:if="{{length > 5}}"> </view>`
- Object attribute access and array indexing: `{{object.key}} {{array[0]}}`
- Object and array literals `{{[zero, 1, 2, 3, 4]}} {{foo: a, bar: b}}`  
  (here `zero`, `a` and `b` are variables in `data`) 

### More templating control syntax

Control syntax are expressed using the attribute `wx:if` and `wx:for` in wxml elements.
`<block>` tags can define blocks of wxml code that appear in different control conditions.

**Conditionals**

Conditionals use the `wx:if` attribute. The value of the attribute must be enclosed in `{{ }}`.

```xml
<view wx:if="{{condition}}"> True </view>

<view wx:if="{{length > 5}}"> 1 </view>
<view wx:elif="{{length > 2}}"> 2 </view>
<view wx:else> 3 </view>

<block wx:if="{{true}}">
  <view> view1 </view>
  <view> view2 </view>
</block>
```

**For loops**

Conditionals use the `wx:for` attribute. The value of the attribute must be enclosed in `{{ }}`.
Again, we may use `<block>` tags to manage blocks of wxml code.

The block with the `wx:for` attribute is repeated for each element in the array. Inside the block, we may
access the index and each element using the variable names `index` and `item`, used by default. We may
change these variable names by specifying `wx:for-index` and `wx:for-item` attributes.

Nested for loops are supported.

```xml
<view wx:for="{{array}}">
  {{index}}: {{item.message}}
</view>

<block wx:for="{{[1, 2, 3]}}">
  <view> {{index}}: </view>
  <view> {{item}} </view>
</block>

<view wx:for="{{array}}" wx:for-index="idx" wx:for-item="itemName">
  {{idx}}: {{itemName.message}}
</view>

<view wx:for="{{[1, 2, 3, 4, 5, 6, 7, 8, 9]}}" wx:for-item="i">
  <view wx:for="{{[1, 2, 3, 4, 5, 6, 7, 8, 9]}}" wx:for-item="j">
    <view wx:if="{{i <= j}}">
      {{i}} * {{j}} = {{i * j}}
    </view>
  </view>
</view>
```

**The `wx:key` attribute in for loops**

We need to specify this attribute when the contents of the for loop may be dynamically changed.

The `wx:key` attribute is often given as the name of an attribute that can uniquely identify an
item in the array. For example:

```javascript
Page({
  data: {
    objectArray: [
      {id: 5, unique: 'unique_5'},
      {id: 4, unique: 'unique_4'},
      {id: 3, unique: 'unique_3'},
      {id: 2, unique: 'unique_2'},
      {id: 1, unique: 'unique_1'},
      {id: 0, unique: 'unique_0'},
    ],
    numberArray: [1, 2, 3, 4]
  }
  // ......
)
```

Corresponding wxml:

```xml
<switch wx:for="{{objectArray}}" wx:key="unique" style="display: block;"> {{item.id}} </switch>
<button bindtap="switch"> Switch </button>
<button bindtap="addToFront"> Add to the front </button>
```

The `switch` tag is repeated for each element in `objectArray`.

## Coordination between wxml and js

### Binding events that happen to wxml elements

Use the `bindtap` attribute to specify the function that will be executed when an item is tapped:

```xml
<view bindtap="myFunc"> ... </view>
```

where `myFunc` is the name of a method defined in the `Page` object.


### Setting and getting attributes associated with wxml elements

By binding a js function to a wxml element's event, the function may take an optional parameter (usually 
denoted as `e`) that contains information about the event, including info about the element that triggered it.

That element is accessed using `e.currentTarget`

**Accessing `data` attributes**

Similar to HTML, we may associate data with wxml elements, fill the data attribute using templating,
and access the data in js code. This is accessed by `e.currentTarget.dataset.[data_field_name]` where in the 
wxml element the data attribute is `<data-[data_field_name]="..."`.

```xml
<view data-myid="{{item.id}}" bindtap="myFunc"> ... </view>
```

```js
// in the definition of the Page object:
Page({
    // ...
    myFunc: function (e) {
        var id_from_wxml_data = e.currentTarget.dataset.myid;
        console.log(id_from_wxml_data);
    }
})
```

### Setting and getting `data` variables stored in the `Page` object in javascript

**In js code:**

```javascript
Page({
    data: {
        myvar: 0,
        myvar2: "hello"
    },
    // ......
    foo: function () {
        var old_myvar = this.data.myvar;
        var old_myvar2 = this.data.myvar2;
        this.setData({
            myvar: old_myvar + 1,
            myvar2: old_myvar2 + " and goodbye"
        });
    },
    myFunc: function() {
        this.setData({
            myvar: this.data.myvar + 10
        });
    }
})

```

## Defining behavior of a page through js

### Events associated with the page

Each event is an attribute in the object that is passed into the constructor of `Page`

#### `onLoad: function (e) {}`

Event that happens when the page loads.

#### `onShow: function (e) {}`

Event that happens when the page is displayed in the user's view.

## Common API methods: linking and web requests

### Linking to another page when tapping on a button (similar to `<a href="...">` in html)

This is done by binding a js function to an element using the `bindtap` attribute for wxml elements. 
The js function then calls the `wx.navigateTo()` method. Example:

```xml
<view bindtap="toIndex"> ... </view>
```

```js
// in the definition of the Page object:
Page({
    // ...
    toIndex: function () {
        wx.navigateTo({
            url: "/url/to/Index"
        });
    }
})
```

### HTML requests `wx.request`

See https://developers.weixin.qq.com/miniprogram/dev/api/network/request/wx.request.html

```javascript
wx.request({
  url: 'url/to/backend/host', //仅为示例，并非真实的接口地址
  method: 'POST',
  data: {
    x: '',
    y: ''
  },
  header: {
    'content-type': 'application/json' // 默认值
  },
  success: function (res) {
    console.log(res.data)
  }
})
```
