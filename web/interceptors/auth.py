from flask import request, g, redirect
import re

from application import app
from common.models.user import User
from common.models.member import Member
from common.libs.user_utils import generate_auth_code as generate_user_auth_code
from common.libs.member_utils import generate_auth_code as generate_member_auth_code
from common.libs.url_utils import build_url
from common.libs.utils import json_error_response
from common.libs.log_utils import *


@app.before_request
def user_auth():
    # filter out urls that do not need to check cookie login info
    pattern = re.compile("|".join(app.config["IGNORE_COOKIE_AUTH_URLS"]))
    if pattern.match(request.path):
        return

    g.current_user = check_login()
    if g.current_user is not None:
        app.logger.info("[user_auth()] User is logged in by checking cookies")
    else:
        app.logger.info("[user_auth()] User is not logged in")
        return redirect(build_url("/user/login"))

    add_access_log(request, g)

def check_login():
    cookie_name = app.config["AUTH_COOKIE_NAME"]
    cookies = request.cookies
    if cookie_name not in cookies:
        return None

    cookie_values = request.cookies[cookie_name].split('#')
    if len(cookie_values) != 2:
        return None

    auth_code, uid = cookie_values[0], cookie_values[1]

    user_info = User.query.filter_by(uid=uid).first()
    if user_info is None \
        or auth_code != generate_user_auth_code(user_info) \
        or user_info.status != 1:
        return None

    return user_info

@app.before_request
def api_member_auth():
    pattern = re.compile("^/api")
    if not pattern.match(request.path):
        return
    pattern = re.compile("|".join(app.config["IGNORE_API_AUTH_URLS"]))
    if pattern.match(request.path):
        return

    member_info = check_api_login()
    if member_info:
        g.member_info = member_info
        app.logger.info("[%s - api_member_auth()] User is logged in by checking cookies" % request.path)
    else:
        app.logger.info("[%s - api_member_auth()] User is not yet logged in " % request.path)
        return json_error_response("用户未登录！")

def check_api_login():
    if "Authorization" not in request.headers:
        return None
    auth_token = request.headers.get("Authorization")
    auth_token_values = auth_token.split("#")
    if len(auth_token_values) != 2:
        return None
    auth_code, member_id = auth_token_values[0], int(auth_token_values[1])

    member_info = Member.query.filter_by(id=member_id).first()

    if member_info is None \
        or auth_code != generate_member_auth_code(member_info) \
        or member_info.status != 1:
        return None

    return member_info