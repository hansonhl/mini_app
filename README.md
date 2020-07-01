# Web App for Wechat Mini Application

This is a practice project from this imooc web development course 
https://coding.imooc.com/learn/list/265.html

All static files (`web/static`) and front-end design files for the 
miniapp (`mina/*`) are provided by the instructor.

## Usage

How to run server in development mode

`$ ./run_dev_server.sh`

## Project Structure

### Admin end

#### Admin Account management 
All backend python code is in `controllers/account/account.py`

- List all accounts using pagination (`templates/account/index.html`, `static/js/account/index.js`)
- List detailed account info and access log (`templates/account/info.html`)
- Adding and editing accounts (`templates/account/set.html`, `static/js/account/set.js`): functions are integrated together
- Deleting and recovering accounts (`templates/account/index.html`, `static/js/account/index.js`)

#### Credentials and authentication
All backend python code is in `controllers/user/user.py`, some helper functions defined in `common/libs/user_utils.py`

- Login (`templates/user/login.html`, `static/js/user/login.js`)
- Edit account info (`templates/user/edit.html`, `static/js/user/edit.js`)
- Reset password (`templates/user/reset_pwd.html`, `static/js/user/reset_pwd.js`)

#### Wechat login

`mina/app.js` defines a lot of helper functions such as:
- `app.console()` for logging
- `app.getRequestHeader()` to allow request data from front end to back end be treated as an html form, 
- `app.buildUrl()` as a general url manager
- `app.getCache()` and `app.setCache()` to store cookie-type data locally in wechat front end

**Functions**

- Frontend login interface and logic (`mina/pages/index/{index.js, index.wxml}`):
    1. First send request to backend to see if user has logged in before (`index.js: checkLogin()`), if yes, redirect to
    `food/index` (`index.js: goToIndex()`)
    2. If user has not logged in before, send request to backend
- Backend member management (`controllers/api/member.py`)
    Some helper functions defined in `common/libs/member_utils.py`
    1. Front end request provides `login_code`, passes this on to WeChat official API to obtain `openid` which is a 
    user's unique identifier per WeChat application.
    2. Registers new members by adding new entries to databases Member and OauthMemberBind