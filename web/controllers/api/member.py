from flask import request, jsonify

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response

from application import app, db

@api_blueprint.route("/member/login", methods=["GET", "POST"])
def login():
    values = request.values
    login_code = values.get("code", "")
    if len(login_code) < 1:
        return json_error_response("需要login_code")

    # complete login process using login_code

    url = "https://api.weixin.qq.com/sns/jscode2session?appid=APPID&secret=SECRET&js_code=JSCODE&grant_type=authorization_code"
    return json_response("success")