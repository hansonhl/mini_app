from flask import request, g
from decimal import Decimal
import json

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, get_current_time, get_int
from common.libs.url_utils import build_image_url
from common.libs.cart_utils import set_cart_info, delete_cart_info

from common.models.member_cart import MemberCart
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

@api_blueprint.route("/cart/delete", methods=["POST"])
def cart_delete():
    if g.current_member is None:
        return json_error_response("请先登录再删除菜品")
    if g.current_member.status != 1:
        return json_error_response("该账户已被注销，无法删除菜品")
    member_id = g.current_member.id

    deleted_list = request.form.get("deleted", None)
    if deleted_list is None:
        return json_error_response("菜品删除操作有误")
    else:
        deleted_list = list(json.loads(deleted_list))

    if deleted_list is None or len(deleted_list) < 1:
        return json_error_response("菜品删除操作有误")

    app.logger.debug("deleted_list %s" % str(deleted_list))
    if not delete_cart_info(member_id, deleted_list):
        return json_error_response("菜品删除操作遇到错误")
    else:
        return json_response("成功从购物车删除%d件菜品" % len(deleted_list))

@api_blueprint.route("/cart/index", methods=["GET"])
def cart_index():
    if g.current_member is None:
        return json_error_response("您需要登录才能使用购物车！")
    if g.current_member.status != 1:
        return json_error_response("该账户已被注销，无法使用购物车")
    member_id = g.current_member.id

    cart_info_list = MemberCart.query.filter_by(member_id=member_id).all()
    if cart_info_list is None:
        data = {
            "list": None
        }
        return json_response(data=data)

    # this is different from what the imooc course does
    cart_food_info_list = db.session.query(MemberCart, Food)\
        .filter(MemberCart.food_id == Food.id).all()

    cart_list = [{
        "id": cart_info.id,
        "food_id": food_info.id,
        "pic_url": build_image_url(food_info.main_image),
        "name": food_info.name,
        "price": str(food_info.price),
        "quantity": cart_info.quantity,
        "active": True
    } for cart_info, food_info in cart_food_info_list]

    app.logger.info("length of list %d" % len(cart_list))
    total_price = sum(float(item["price"]) for item in cart_list)

    data = {
        "list": cart_list,
        "totalPrice": str(Decimal(total_price).quantize(Decimal("0.00"))),
    }

    return json_response(data=data)
