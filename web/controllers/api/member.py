from flask import request, jsonify
import requests, json

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, get_current_time
from common.libs.member_utils import generate_salt, get_wechat_openid, generate_token
from common.models.member import Member
from common.models.oauth_member_bind import OauthMemberBind

from application import app, db

@api_blueprint.route("/member/login", methods=["GET", "POST"])
def login():
    """Complete login process:
    1. mina/pages/index/index.js: Page.login() --> request with login_code --> this server
    3. this function --> request with appid, appSecretKey, login_code --> wechat official api
    4. wechat official api --> session_key, openid --> this server
    """
    values = request.values
    login_code = values.get("login_code", "")
    if len(login_code) < 1:
        return json_error_response("需要login_code")

    # complete login process using login_code
    openid = get_wechat_openid(login_code)
    if openid is None:
        return json_error_response("调用微信登录信息出错")

    # check if user has registered
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first() # type=1 corresponds to wechat
    if bind_info:
        # member exists
        member_info = Member.query.filter_by(id=bind_info.member_id).first()
        if not member_info:
            return json_error_response("查询不到后台用户信息")
        return json_response("已经绑定成功", data={"token": generate_token(member_info)})
    else:
        # register new member
        new_member = Member()
        new_member.nickname = values.get("nickName", "")
        new_member.sex = values.get("gender", 0)
        new_member.avatar = values.get("avatarUrl", "")
        new_member.salt = generate_salt()
        new_member.updated_time = new_member.created_time = get_current_time()
        db.session.add(new_member)
        db.session.commit()

        # bind new member with new OathMemberBind entry
        new_bind = OauthMemberBind()
        new_bind.member_id = new_member.id
        new_bind.type = 1
        new_bind.openid = openid
        new_bind.extra = ""
        new_bind.updated_time = new_bind.created_time = get_current_time()
        db.session.add(new_bind)
        db.session.commit()
        return json_response("新用户注册成功", data={"token": generate_token(new_member)})

@api_blueprint.route("/member/check-reg", methods = ["GET", "POST"])
def check_reg():
    values = request.values
    login_code = values.get("login_code", "")
    if len(login_code) < 1:
        return json_error_response("需要login_code")

    openid = get_wechat_openid(login_code)
    if openid is None:
        return json_error_response("调用微信登录信息出错")

    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first() # type=1 corresponds to wechat
    if not bind_info:
        return json_error_response("未绑定")

    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    if not member_info:
        return json_error_response("查询不到对应的用户信息")

    # similar function to cookies, token is saved in front end so we may save login status
    return json_response("登录成功", data={"token": generate_token(member_info)})

@api_blueprint.route("/memnber/share", methods=["POST"])
def member_share():

    return json_response()
