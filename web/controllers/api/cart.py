from flask import request, g
import math
from sqlalchemy import or_

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, get_current_time, get_int
from common.libs.cart_utils import set_cart_info, delete_cart_info

from common.models.food import Food


from application import app, db

@api_blueprint.route("/cart/set", methods=["POST"])
def cart_set():
    if g.current_member is None:
        return json_error_response("请先登录再添加菜品至购物车")
    if g.current_member.status != 1:
        return json_error_response("该账户已被注销，无法添加菜品至购物车")
    member_id = g.current_member.id

    food_id = get_int(request.form, "food_id", 0)
    food_info = Food.query.filter_by(id=food_id).first()
    if food_id < 1 or food_info is None:
        return json_error_response("该菜品不存在")

    quantity = get_int(request.form, "quantity", None)
    if quantity is None or quantity < 0:
        return json_error_response("请提供正确的菜品数量")

    if food_info.stock < quantity:
        return json_error_response("该菜品库存不足")

    if quantity > 0:
        cart_info = set_cart_info(member_id, food_id, quantity)
        if cart_info is None:
            return json_error_response("添加至购物车失败")
        else:
            return json_response("成功添加菜品至购物车")
    else:
        if delete_cart_info(member_id, food_id):
            return json_error_response("删除菜品失败")
        else:
            return json_response("成功从购物车删除菜品")

