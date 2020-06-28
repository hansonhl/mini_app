import datetime
from flask import render_template, jsonify, make_response, g

def get_current_time(fmt="%Y-%m-%d %H-%M-%S"):
    dt = datetime.datetime.now()
    return dt.strftime(fmt)

def render_template_with_global_vars(template, context={}):
    if "current_user" in g and g.current_user is not None:
        context["current_user"] = g.current_user
    return render_template(template, **context)

def json_response(code=200, msg="Success!", data={}):
    res = {"code": code, "msg": msg, "data": data}
    return make_response(jsonify(res))

def json_error_response(msg="An error occurred", data={}):
    return json_response(code=-1, msg=msg, data=data)