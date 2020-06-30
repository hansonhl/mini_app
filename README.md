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
All backend python code is in `controllers/user/user.py`

- Login (`templates/user/login.html`, `static/js/user/login.js`)
- Edit account info (`templates/user/edit.html`, `static/js/user/edit.js`)
- Reset password (`templates/user/reset_pwd.html`, `static/js/user/reset_pwd.js`)