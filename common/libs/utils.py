import datetime, math
from flask import render_template, jsonify, make_response, g

def get_current_time(fmt="%Y-%m-%d %H:%M:%S"):
    dt = datetime.datetime.now()
    return dt.strftime(fmt)

def render_template_with_global_vars(template, context={}):
    if "current_user" in g and g.current_user is not None:
        context["current_user"] = g.current_user
    return render_template(template, **context)

def json_response(msg="Success!", code=200, data={}):
    res = {"msg": msg, "code": code, "data": data}
    return make_response(jsonify(res))

def json_error_response(msg="An error occurred", data={}):
    return json_response(msg=msg, code=-1, data=data)

def pagination(num_items, items_per_page, current_page, url):
    num_pages = max(1, math.ceil(num_items / items_per_page))

    pagination_dict = {
        "current_page": current_page,
        "num_pages": num_pages,
        "num_items": num_items,
        "items_per_page": items_per_page,
        "has_prev": current_page > 1,
        "has_next": current_page < num_pages,
        "range": range(1, num_pages + 1),
        "url": url
    }

    return pagination_dict
