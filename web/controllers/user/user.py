from flask import Blueprint, render_template, request, make_response,  redirect, g
from application import app, db

from common.models.user import User
from common.libs.utils import json_response, json_error_response, render_template_with_global_vars
from common.libs.user_utils import generate_salted_pwd, generate_cookie
from common.libs.url_manager import build_url

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("user/login.html")
    else:
        username =  request.form["login_name"] if "login_name" in request.form else ""
        pwd = request.form["login_pwd"] if "login_pwd" in request.form else ""

        if username is None or len(username) < 1 or pwd is None or len(pwd) < 1:
            return json_error_response("Your username or password should not be empty!")

        user_info = User.query.filter_by(login_name=username).first()

        if user_info is None:
            return json_error_response("Your username or password is incorrect!")

        salted_pwd = generate_salted_pwd(pwd, user_info.login_salt)
        if salted_pwd != user_info.login_pwd:
            return json_error_response("Your username or password is incorrect!")

        if user_info.status != 1:
            return json_error_response("Your account has either been suspended or terminated")

        response = json_response(msg="You've logged in successfully!")
        response.set_cookie(app.config["AUTH_COOKIE_NAME"], generate_cookie(user_info))
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

        user_info = g.current_user
        user_info.nickname = nickname
        user_info.email = email
        db.session.add(user_info)
        db.session.commit()

        res_data = {"nickname": nickname, "email": email}

        return json_response(msg="账号个人信息编辑成功!", data=res_data)



@user_blueprint.route("/reset_pwd")
def reset_pwd():
    return render_template_with_global_vars("user/reset_pwd.html")

