from flask import request, g, redirect
import re

from application import app
from common.models.user import User
from common.libs.user_utils import generate_auth_code
from common.libs.url_manager import build_url
from common.libs.log_service import *


@app.before_request
def before_request():
    # filter out urls that do not need to check cookie login info
    pattern = re.compile("|".join(app.config["IGNORE_COOKIE_AUTH_URLS"]))

    if pattern.match(request.path):
        return

    g.current_user = check_login()
    if g.current_user is not None:
        app.logger.info("[before_request()] User is logged in by checking cookies")
    else:
        app.logger.info("[before_request()] User is not logged in")
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
    if user_info is None:
        return None

    if auth_code != generate_auth_code(user_info):
        return None

    if user_info.status != 1:
        return None

    return user_info