from flask import Blueprint, request, make_response, redirect
from sqlalchemy import or_

from application import app, db

from common.libs.url_manager import build_url
from common.libs.utils import render_template_with_global_vars, pagination, json_error_response, json_response
from common.libs.utils import get_current_time
from common.libs.user_utils import generate_salted_pwd, generate_salt
from common.models.user import User
from common.models.app_access_log import AppAccessLog

account_blueprint = Blueprint("account", __name__)

@account_blueprint.route("/index")
def index():
    current_page = int(request.args.get("p", "1"))
    values = request.values
    users_per_page = app.config["MEMBER_INDEX_ITEMS_PER_PAGE"]

    user_info_query = User.query

    # filtering by search
    if "mix_kw" in values and len(values["mix_kw"]) > 0:
        app.logger.debug("mix_kw %s" % values["mix_kw"])
        rule = or_(User.nickname.ilike("%%%s%%" % values["mix_kw"]),
                   User.mobile.ilike("%%%s%%" % values["mix_kw"]))
        user_info_query = user_info_query.filter(rule)

    # pagination
    offset = (current_page - 1) * users_per_page
    pagination_dict = pagination(num_items=user_info_query.count(),
                                 items_per_page=users_per_page,
                                 current_page=current_page,
                                 url=build_url("/account/index?"))
    user_info_list = user_info_query[offset:offset+users_per_page]
    page_params = {"user_info_list": user_info_list,
                   "pagination": pagination_dict,
                   "search": {"mix_kw": values.get("mix_kw", None),
                              "status": values.get("status", "-1")},
                   "status_mapping": app.config["ACCOUNT_STATUS_MAPPING"]}

    return render_template_with_global_vars("account/index.html", context=page_params)

@account_blueprint.route("/info")
def info():
    uid = int(request.args["uid"]) if "uid" in request.args else None

    # redirect if uid is invalid or empty
    redir_response = make_response(redirect(build_url("/account/index")))
    if uid is None:
        return redir_response
    user_info = User.query.filter_by(uid = uid).first()
    if user_info is None:
        return redir_response

    # access log
    access_log_num_entries = 30
    access_log_query = AppAccessLog.query.order_by(AppAccessLog.created_time.desc())
    access_log = access_log_query.filter_by(uid=uid).all()[:access_log_num_entries]

    return render_template_with_global_vars("account/info.html", context={"user": user_info,
                                                                          "num_entries": len(access_log),
                                                                          "access_log": access_log})

@account_blueprint.route("/set", methods=["GET", "POST"])
def set():
    default_pwd = "******"
    if request.method == "GET":
        # pass user info into template to fill in values of html form
        uid = request.args["uid"] if "uid" in request.args else None
        user_info = User.query.filter_by(uid=uid).first() if uid else None
        ctx = {"user": user_info, "default_pwd": default_pwd}
        return render_template_with_global_vars("account/set.html", context=ctx)

    elif request.method == "POST":
        # obtain info from form
        uid = int(request.form["uid"]) if "uid" in request.form else 0
        username = request.form["login_name"] if "login_name" in request.form else ""
        pwd = request.form["login_pwd"] if "login_pwd" in request.form else ""
        nickname = request.form["nickname"] if "nickname" in request.form else ""
        mobile = request.form["mobile"] if "mobile" in request.form else ""
        email = request.form["email"] if "email" in request.form else ""
        app.logger.debug("setting info for uid %d, new username %s, pwd %s" % (uid, username, pwd))

        # validate form elements
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
            return json_error_response(msg)
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
        if pwd != default_pwd:
            user_info.login_pwd = generate_salted_pwd(pwd, user_info.login_salt)

        db.session.add(user_info)
        db.session.commit()

        return json_response("账号个人信息编辑成功!", data={})

@account_blueprint.route("/ops", methods=["POST"])
def ops():
    values = request.values
    if "act" not in values or "uid" not in values:
        return json_error_response("无效的账号编辑操作")

    user_info = User.query.filter_by(uid=values["uid"]).first()

    if not user_info:
        return json_error_response("无效的账号编辑操作")

    if values["act"] == "remove":
        user_info.status = 0
        success_msg = "成功移除 %s 的账户 (登录名 %s)" % (user_info.nickname, user_info.login_name)
    elif values["act"] == "recover":
        success_msg = "成功恢复 %s 的账户 (登录名 %s)" % (user_info.nickname, user_info.login_name)
        user_info.status = 1
    else:
        return json_error_response("无效的账号编辑操作")

    user_info.update_time = get_current_time()

    db.session.add(user_info)
    db.session.commit()

    return json_response(success_msg)

