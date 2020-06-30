from flask import Blueprint, render_template, request, make_response,  redirect, g
from application import app, db

from common.models.user import User
from common.libs.utils import json_response, json_error_response, render_template_with_global_vars
from common.libs.user_utils import generate_salted_pwd, generate_cookie, check_login
from common.libs.url_manager import build_url

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("user/login.html")
    else:
        error_response, user_info = check_login(request)
        if error_response:
            return error_response
        response = json_response(msg="You've logged in successfully!")
        response.set_cookie(app.config["AUTH_COOKIE_NAME"], generate_cookie(user_info), 60*60*24*30)
        return response

@user_blueprint.route("/logout")
def logout():
    g.current_user = None
    response = make_response(redirect(build_url("/user/login")))
    response.delete_cookie(app.config["AUTH_COOKIE_NAME"])
    return response

@user_blueprint.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "GET":
        return render_template_with_global_vars("user/edit.html")
    elif request.method == "POST":
        nickname = request.form["nickname"] if "nickname" in request.form else ""
        email = request.form["email"] if "email" in request.form else ""

        if "current_user" not in g or g.current_user is None:
            return json_error_response("您还没有登录，不能更改个人信息!")

        if len(nickname) < 1 or len(email) < 1:
            return json_error_response("您的姓名或邮箱不能为空!")

        user_info = g.current_user
        user_info.nickname = nickname
        user_info.email = email
        db.session.add(user_info)
        db.session.commit()

        res_data = {"nickname": nickname, "email": email}

        return json_response(msg="账号个人信息编辑成功!", data=res_data)



@user_blueprint.route("/reset_pwd", methods=["POST", "GET"])
def reset_pwd():
    if request.method == "GET":
        return render_template_with_global_vars("user/reset_pwd.html")
    elif request.method == "POST":
        old_pwd = request.form["old_pwd"] if "old_pwd" in request.form else ""
        new_pwd = request.form["new_pwd"] if "new_pwd" in request.form else ""

        if len(old_pwd) < 1 or len(new_pwd) < 1:
            return json_error_response("您输入的密码不能为空!")

        if len(new_pwd) < 6:
            return json_error_response("您的密码不能短于6个字符！")

        if "current_user" not in g or g.current_user is None:
            return json_error_response("您还没有登录，不能更改个人信息!")

        # check old password
        user_info = g.current_user
        if generate_salted_pwd(old_pwd, user_info.login_salt) != user_info.login_pwd:
            return json_error_response("您输入的旧密码不正确!")

        user_info.login_pwd = generate_salted_pwd(new_pwd, user_info.login_salt)
        db.session.add(user_info)
        db.session.commit()

        response = json_response(msg="修改密码成功!")
        response.set_cookie(app.config["AUTH_COOKIE_NAME"], generate_cookie(user_info), 60*60*24*30)
        return response


