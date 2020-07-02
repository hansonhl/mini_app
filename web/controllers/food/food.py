from flask import Blueprint, request, make_response, redirect
from common.libs.utils import render_template_with_global_vars, json_error_response, json_response, get_current_time
from common.libs.utils import pagination
from common.libs.url_manager import build_url
from common.models.food_cat import FoodCat

from application import app, db

food_blueprint = Blueprint("food", __name__)

@food_blueprint.route("/index")
def index():
    return render_template_with_global_vars("food/index.html")

@food_blueprint.route("/info")
def info():
    return render_template_with_global_vars("food/info.html")

@food_blueprint.route("/set")
def set():
    return render_template_with_global_vars("food/set.html")

@food_blueprint.route("/cat")
def cat():
    current_page = int(request.args.get("p", "1"))
    values = request.values
    items_per_page = app.config["FOOD_CAT_ITEMS_PER_PAGE"]

    food_cat_query = FoodCat.query.order_by(FoodCat.status.desc(), FoodCat.weight.desc())

    # filtering by status
    if "status" in values:
        if values["status"] != "-1":
            food_cat_query = food_cat_query.filter_by(status=int(values["status"]))

    # pagination
    offset = (current_page - 1) * items_per_page
    pagination_dict = pagination(num_items=food_cat_query.count(),
                                 items_per_page=items_per_page,
                                 current_page=current_page,
                                 url=build_url("/food/cat?"))
    food_cat_info_list = food_cat_query.offset(offset).limit(items_per_page).all()

    page_params = {"food_cat_info_list": food_cat_info_list,
                   "pagination": pagination_dict,
                   "search": {"status": values.get("status", "-1")},
                   "status_mapping": app.config["ACCOUNT_STATUS_MAPPING"]}

    return render_template_with_global_vars("food/cat.html", context=page_params)

@food_blueprint.route("/cat_set", methods=["GET", "POST"])
def cat_set():
    if request.method == "GET":
        id = int(request.args.get("id", "0"))
        if id > 0:
            cat_info = FoodCat.query.filter_by(id=id).first()
            if cat_info is None:
                return make_response(redirect(build_url("/food/cat")))
        else:
            cat_info = None
        return render_template_with_global_vars("food/cat_set.html", context={"cat": cat_info})

    elif request.method == "POST":
        id = int(request.form.get("id", "0"))
        if id > 0:
            cat_info = FoodCat.query.filter_by(id=id).first()
            if cat_info is None:
                return json_error_response("无效的食品类别编辑操作")
        else:
            cat_info = None

        name = request.form.get("name", "")
        weight = int(request.form.get("weight", "0"))
        if len(name) < 1:
            return json_error_response("食品类别名称不能为空！")
        if weight < 1 or weight > 4:
            return json_error_response("食品类别的权重必须在1-4之间！（含1和4）")

        if cat_info is None:
            cat_info = FoodCat()
            cat_info.created_time = get_current_time()
            cat_info.status = 1

        cat_info.name = name
        cat_info.weight = weight
        cat_info.updated_time = get_current_time()
        db.session.add(cat_info)
        db.session.commit()

        return json_response("修改食品类别信息成功！")

@food_blueprint.route('/cat_ops', methods=["POST"])
def cat_ops():
    values = request.form
    if "act" not in values or "id" not in values:
        return json_error_response("无效的食品类别编辑操作")

    food_cat_info = FoodCat.query.filter_by(id=values["id"]).first()

    if not food_cat_info:
        return json_error_response("无效的账号编辑操作")

    if values["act"] == "remove":
        food_cat_info.status = 0
        success_msg = "成功移除食品类别 %s" % (food_cat_info.name)
    elif values["act"] == "recover":
        success_msg = "成功恢复食品类别 %s" % (food_cat_info.name)
        food_cat_info.status = 1
    else:
        return json_error_response("无效的账号编辑操作")

    food_cat_info.update_time = get_current_time()

    db.session.add(food_cat_info)
    db.session.commit()

    return json_response(success_msg)