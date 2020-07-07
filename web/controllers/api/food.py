from flask import request
import math
from sqlalchemy import or_

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, get_current_time, get_int
from common.libs.url_utils import build_image_url
from common.models.food import Food
from common.models.food_cat import FoodCat

from application import app, db

@api_blueprint.route("/food/index")
def food_index():
    # get food info from database
    food_cat_info_list = FoodCat.query.filter_by(status=1).order_by(FoodCat.weight.desc()).all()
    food_cat_list = [{"id": 0, "name": "全部"}]
    if food_cat_info_list:
        food_cat_list = food_cat_list + [{"id": cat.id, "name": cat.name}
                                         for cat in food_cat_info_list]
    else:
        food_cat_list = None

    food_info_list = Food.query.filter_by(status=1).order_by(Food.total_count.desc(), Food.id).limit(3).all()
    if food_info_list:
        food_list = [{"id": food.id, "name": food.name, "pic_url": build_image_url(food.main_image)}
                     for food in food_info_list]
    else:
        food_list = None

    data = {
        "bannerList": food_list,
        "catList": food_cat_list
    }

    return json_response(data=data)

@api_blueprint.route("/food/search")
def food_search():
    values = request.values
    cat_id = get_int(values, "cat_id", 0)
    mix_kw = values.get("mix_kw", "")
    current_page = get_int(values, "p", 1)

    food_info_query = Food.query.filter_by(status=1)
    if len(mix_kw) > 0:
        pattern = "%%%s%%" % values["mix_kw"]
        rule = or_(Food.name.ilike(pattern), Food.tags.ilike(pattern))
        food_info_query = food_info_query.filter(rule)
    if cat_id > 0:
        food_info_query = food_info_query.filter_by(cat_id=cat_id)

    num_items = food_info_query.count()
    items_per_page = app.config["APP_FOOD_INDEX_ITEMS_PER_PAGE"]
    offset = (current_page - 1) * items_per_page
    food_info_query = food_info_query.order_by(Food.total_count.desc(), Food.id.desc())
    food_info_list = food_info_query.offset(offset).limit(items_per_page).all()

    food_list = []
    if food_info_list:
        food_list = [{"id": food.id, "name": food.name, "price": str(food.price),
                      "min_price": str(food.price), "pic_url": build_image_url(food.main_image)
                      } for food in food_info_list]

    data = {"list": food_list,
            "has_next_page": math.ceil(num_items / items_per_page) > current_page}
    return json_response(data=data)

@api_blueprint.route("/food/info")
def food_info():
    values = request.values
    food_id = get_int(values, "id", 0)
    if food_id == 0:
        return json_error_response("该菜品不存在！")

    food_info = Food.query.filter_by(id=food_id).first()
    if food_info is None:
        return json_error_response("该菜品不存在！")
    if food_info.status != 1:
        return json_error_response("该菜品已下架！")

    main_image_url = build_image_url(food_info.main_image)
    data = {
                "id": food_id,
                "name": food_info.name,
                "summary": food_info.summary,
                "total_count": food_info.total_count,
                "comment_count": food_info.comment_count,
                "stock": food_info.stock,
                "price": str(food_info.price),
                "main_image": main_image_url,
                "pics": [main_image_url]
            }
    return json_response(data={"info": data})
