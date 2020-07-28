import datetime, math
from application import app
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


def get_id_to_model_dict(db_model, id_field, filter_by=None, filter_list=None):
    """ If select_list is none, equivalent to:
            SELECT * from db_model
        If it is not none, equivalent to:
            SELECT * from db_model WHERE filter_by IN filter_list

        organize return result in dict mapping from id_field -> whole row
        id_field is usually "id"
    """
    res = {}
    query = db_model.query
    if filter_by and filter_list and len(filter_list) > 0:
        query = query.filter(filter_by.in_(filter_list))

    l = query.all()
    if l is None:
        return None

    for item in l:
        if not hasattr(item, id_field):
            break
        else:
            res[getattr(item, id_field)] = item
    return res

def get_int(dict, key, default=None):
    res_str = dict.get(key, default)
    try:
        res = int(res_str)
    except ValueError:
        return default
    return res

class require_login:
    def __init__(self, f):
        self._f = f
        self.__name__ = f.__name__

    def __call__(self, *args, **kwargs):
        if g.current_member is None:
            return json_error_response("您没有登录，无法完成该操作")
        if g.current_member.status != 1:
            return json_error_response("该账户已被注销，无法完成该操作")
        return self._f(*args, **kwargs)

def get_addr_idxs(prov_id, city_id, distr_id=0):
    prov_map = app.config["PROV_ID_TO_IDX_MAP"]
    city_map = app.config["CITY_ID_TO_IDX_MAPS"]
    distr_map = app.config["DISTR_ID_TO_IDX_MAPS"]

    prov_idx = prov_map[prov_id]
    city_idx = city_map[prov_idx][city_id]

    distr_idx = 0
    if distr_id > 0:
        distr_idx = distr_map[prov_idx][city_idx][distr_id]

    return prov_idx, city_idx, distr_idx