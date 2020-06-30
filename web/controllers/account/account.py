from flask import Blueprint, request, make_response, redirect

from application import app, db

from common.libs.url_manager import build_url
from common.libs.utils import render_template_with_global_vars, pagination, json_error_response, json_response
from common.libs.utils import get_current_time
from common.libs.user_utils import generate_salted_pwd, generate_salt
from common.models.user import User

account_blueprint = Blueprint("account", __name__)

@account_blueprint.route("/index")
def index():
    current_page = int(request.args["p"]) if "p" in request.args else 1
    users_per_page = app.config["ACCOUNT_INDEX_USERS_PER_PAGE"]
    offset = (current_page - 1) * users_per_page

    user_info_query = User.query

    pagination_dict = pagination(num_items=user_info_query.count(),
                                 items_per_page=users_per_page,
                                 current_page=current_page,
                                 url=build_url("/account/index?"))

    user_info_list = user_info_query[offset:offset+users_per_page]

    page_params = {"user_info_list": user_info_list, "pagination": pagination_dict}
    return render_template_with_global_vars("account/index.html", context=page_params)

@account_blueprint.route("/info")
def info():
    uid = int(request.args["uid"]) if "uid" in request.args else None
    redir_response = make_response(redirect(build_url("/account/index")))
    if uid is None:
        return redir_response

    user_info = User.query.filter_by(uid = uid).first()
    if user_info is None:
        return redir_response

    return render_template_with_global_vars("account/info.html", context={"user": user_info})

@account_blueprint.route("/set", methods=["GET", "POST"])
def set():
    default_pwd = "******"
    if request.method == "GET":
        uid = request.args["uid"] if "uid" in request.args else None
        user_info = User.query.filter_by(uid=uid).first() if uid else None
        ctx = {"user": user_info, "default_pwd": default_pwd}
        return render_template_with_global_vars("account/set.html", context=ctx)

    elif request.method == "POST":
        uid = int(request.form["uid"]) if "uid" in request.form else 0
        username = request.form["login_name"] if "login_name" in request.form else ""
        pwd = request.form["login_pwd"] if "login_pwd" in request.form else ""
        nickname = request.form["nickname"] if "nickname" in request.form else ""
        mobile = request.form["mobile"] if "mobile" in request.form else ""
        email = request.form["email"] if "email" in request.form else ""
        app.logger.debug("setting info for uid %d, new username %s" % (uid, username))

        if len(nickname) < 1 or len(email) < 1 or len(mobile) < 1:
            empty_items = []
            if len(nickname) < 1:
                empty_items.append("姓名")
            if len(mobile) < 1:
                empty_items.append("手机")
            if len(email) < 1:
                empty_items.append("邮箱")
            if len(username) < 1:
                empty_items.append("登录名")
            if len(pwd) < 1:
                empty_items.append("登录密码")

            msg = "以下内容不能为空：" + "、".join(empty_items)
            return json_error_response(msg=msg)

        if len(pwd) < 6 and uid == 0:
            return json_error_response("您的密码不能短于6个字符！")

        user_info = User.query.filter(User.login_name == username, User.uid != uid).first()
        if user_info:
            return json_error_response("该用户名已被使用，请使用别的用户名！")

        user_info = User.query.filter_by(uid = uid).first()
        app.logger.debug("uid %d user_info %s" % (uid, user_info))
        new_user = False
        if user_info is None:
            new_user = True
            user_info = User()
            user_info.login_salt = generate_salt()
            user_info.created_time = get_current_time()

        user_info.login_name = username
        user_info.nickname = nickname
        user_info.mobile = mobile
        user_info.email = email

        # edit password when it is not default value "*****" (see set.html)
        if pwd != "*****":
            user_info.pwd = generate_salted_pwd(pwd, user_info.login_salt)

        db.session.add(user_info)
        db.session.commit()

        if new_user:
            app.logger.debug("Edited user %s" % username)
        else:
            app.logger.debug("Created new user %s" % username)

        return json_response(msg="账号个人信息编辑成功!", data={})