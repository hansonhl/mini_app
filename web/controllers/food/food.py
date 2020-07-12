from flask import Blueprint, request, make_response, redirect
from decimal import Decimal

from common.libs.utils import render_template_with_global_vars, json_error_response, json_response, get_current_time
from common.libs.utils import pagination, get_id_to_model_dict, get_int
from common.libs.url_utils import build_url
from common.libs.food_utils import set_food_stock_change_log

from common.models.food import Food
from common.models.food_cat import FoodCat
from common.models.food_stock_change_log import FoodStockChangeLog

from application import app, db

food_blueprint = Blueprint("food", __name__)

@food_blueprint.route("/index")
def index():
    current_page = get_int(request.args, "p", 1)
    values = request.values
    items_per_page = app.config["FOOD_INDEX_ITEMS_PER_PAGE"]

    food_info_query = Food.query.order_by(Food.status.desc(), Food.id.desc())

    # filtering by search
    if "mix_kw" in values and len(values["mix_kw"]) > 0:
        rule = Food.name.ilike("%%%s%%" % values["mix_kw"])
        food_info_query = food_info_query.filter(rule)

    if "status" in values and values["status"] != "-1":
        food_info_query = food_info_query.filter_by(status=int(values["status"]))

    if "cat_id" in values and values["cat_id"] != "0":
        food_info_query = food_info_query.filter_by(cat_id=int(values["cat_id"]))

    # pagination
    offset = (current_page - 1) * items_per_page
    pagination_dict = pagination(num_items=food_info_query.count(),
                                 items_per_page=items_per_page,
                                 current_page=current_page,
                                 url=build_url("/food/index?"))
    food_info_list = food_info_query.offset(offset).limit(items_per_page).all()

    food_cat_list = FoodCat.query.all()
    food_cat_dict = get_id_to_model_dict(FoodCat, "id", "id")
    page_params = {"food_info_list": food_info_list,
                   "food_cat_list": food_cat_list,
                   "food_cat_dict": food_cat_dict,
                   "pagination": pagination_dict,
                   "search": {"mix_kw": values.get("mix_kw", None),
                              "status": values.get("status", "-1"),
                              "cat_id": values.get("cat_id", "0")},
                   "status_mapping": app.config["ACCOUNT_STATUS_MAPPING"]}

    return render_template_with_global_vars("food/index.html", context=page_params)

@food_blueprint.route('/ops', methods=["POST"])
def ops():
    id = get_int(request.form, "id", 0)
    act = request.form.get("act", None)
    if "act" is None or "id" == 0:
        return json_error_response("无效的菜品项目编辑操作")

    food_info = Food.query.filter_by(id=id).first()

    if not food_info:
        return json_error_response("无效的菜品项目编辑操作")

    if act == "remove":
        food_info.status = 0
        success_msg = "成功移除菜品项目 %s" % (food_info.name)
    elif act == "recover":
        success_msg = "成功恢复菜品项目 %s" % (food_info.name)
        food_info.status = 1
    else:
        return json_error_response("无效的账号编辑操作")

    food_info.update_time = get_current_time()

    db.session.add(food_info)
    db.session.commit()

    return json_response(success_msg)

@food_blueprint.route("/info")
def info():
    id = get_int(request.args, "id", 0)
    redir_response = make_response(redirect(build_url("/food/index")))
    if id == 0:
        return redir_response
    food_info = Food.query.filter_by(id=id).first()
    if food_info is None:
        return redir_response

    stock_change_query = FoodStockChangeLog.query.filter_by(food_id=id)
    stock_change_query = stock_change_query.order_by(FoodStockChangeLog.created_time.desc())
    stock_change_list = stock_change_query.all()

    ctx = {"food": food_info, "stock_change_list": stock_change_list}
    return render_template_with_global_vars("food/info.html", context=ctx)


@food_blueprint.route("/set", methods=["POST", "GET"])
def set():
    if request.method == "GET":
        cat_list = FoodCat.query.all()
        id = get_int(request.args, "id", 0)
        food_info = Food.query.filter_by(id=id).first()
        if (id > 0 and food_info is None) or (food_info is not None and food_info.status != 1):
            return redirect(build_url("/food/index"))

        ctx = {"food": food_info,
               "cat_list": cat_list}
        return render_template_with_global_vars("food/set.html", context=ctx)
    elif request.method == "POST":
        id = get_int(request.form, "id", 0)
        cat_id = get_int(request.form, "cat_id", 0)
        name = request.form.get("name", "")
        price = request.form.get("price", "")
        title_pic = request.form.get("title_pic", "")
        summary = request.form.get("summary", "")
        stock = get_int(request.form, "stock", 0)
        tags = request.form.get("tags", "")

        # form content verification
        if cat_id == 0:
            return json_error_response("请选择类别")
        empty_items = []
        for var, item in zip([name, price, title_pic, summary, tags], ["菜品名称", "菜品价格", "封面图", "描述", "标签"]):
            if len(var) < 1:
                empty_items.append(item)
        if len(empty_items) > 0:
            return json_error_response("以下内容不能为空：" + "、".join(empty_items))

        price = Decimal(price).quantize(Decimal("0.00"))
        if price <= 0:
            return json_error_response("售卖价格不能小于或者等于0")

        # create new entry in Food table
        food_info = Food.query.filter_by(id=id).first()
        before_stock = 0
        if food_info:
            before_stock = food_info.stock
        else:
            food_info = Food()
            food_info.status = 1
            food_info.created_time = get_current_time()

        food_info.cat_id = cat_id
        food_info.name = name
        food_info.price = price
        food_info.main_image = title_pic
        food_info.summary = summary
        food_info.stock = stock
        food_info.tags = tags
        food_info.updated_time = get_current_time()

        db.session.add(food_info)
        db.session.commit()

        # add entry into food stock change log
        if not set_food_stock_change_log(food_info.id, int(before_stock),
                                         int(stock) - int(before_stock), "后台直接更改"):
            return json_error_response("登记库存变更信息出现错误")

        return json_response("成功添加菜品 %s" % name)



@food_blueprint.route("/cat")
def cat():
    current_page = get_int(request.args, "p", 1)
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
        id = get_int(request.args, "id", 0)
        if id > 0:
            cat_info = FoodCat.query.filter_by(id=id).first()
            if cat_info is None:
                return make_response(redirect(build_url("/food/cat")))
        else:
            cat_info = None
        return render_template_with_global_vars("food/cat_set.html", context={"cat": cat_info})

    elif request.method == "POST":
        id = get_int(request.form, "id", 0)
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
    id = get_int(request.form, "id", 0)
    act = request.form.get("act", None)
    if "act" is None or "id" == 0:
        return json_error_response("无效的菜品项目编辑操作")

    food_cat_info = FoodCat.query.filter_by(id=id).first()

    if not food_cat_info:
        return json_error_response("无效的账号编辑操作")

    if act == "remove":
        food_cat_info.status = 0
        success_msg = "成功移除食品类别 %s" % (food_cat_info.name)
    elif act == "recover":
        success_msg = "成功恢复食品类别 %s" % (food_cat_info.name)
        food_cat_info.status = 1
    else:
        return json_error_response("无效的账号编辑操作")

    food_cat_info.update_time = get_current_time()

    db.session.add(food_cat_info)
    db.session.commit()

    return json_response(success_msg)