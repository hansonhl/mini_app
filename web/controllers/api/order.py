from flask import request, g, jsonify, make_response
from decimal import Decimal
import json

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, get_current_time, get_int
from common.libs.url_utils import build_image_url
from common.libs.cart_utils import delete_cart_info
from common.libs.pay_utils import create_order

from common.models.food import Food
from common.models.pay_order import PayOrder
from common.models.oauth_member_bind import OauthMemberBind

from application import app, db

@api_blueprint.route("/order/info", methods=["POST"])
def order_info():
    purchase_list = request.form.get("purchaseList", None)
    if purchase_list is None:
        return json_error_response("订单内容不能为空！")

    purchase_list = json.loads(purchase_list)
    if len(purchase_list) < 1:
        return json_error_response("订单内容不能为空！")

    food_id_to_quantity = {item["food_id"] : item["quantity"] for item in purchase_list}
    food_ids = food_id_to_quantity.keys()
    food_info_list = Food.query.filter(Food.id.in_(food_ids)).all()
    if len(food_info_list) < 1:
        return json_error_response("无法查询到订单中的菜品！")

    deliver_price = Decimal(5000.00)
    order_list = [{
        "food_id": food.id,
        "name": food.name,
        "price": str(food.price),
        "pic_url": build_image_url(food.main_image),
        "quantity": food_id_to_quantity[food.id],
    } for food in food_info_list]
    pay_price = Decimal(sum(food.price * food_id_to_quantity[food.id] for food in food_info_list))

    default_address = {
        "name": "编程浪子",
        "mobile": "12345678901",
        "address": "上海市浦东新区XX"
    }

    data = {
        "order_list": order_list,
        "deliver_price": str(deliver_price),
        "pay_price": str(pay_price),
        "total_price": str(pay_price + deliver_price),
        "default_address": default_address
    }
    return json_response(data=data)

@api_blueprint.route("/order/create", methods=["POST"])
def order_create():
    if g.current_member is None:
        return json_error_response("请先登录再提交订单")
    if g.current_member.status != 1:
        return json_error_response("该账户已被注销，无法提交订单")
    member_id = g.current_member.id

    order_type = request.form.get("type", None)
    order_list = request.form.get("purchaseList", None)
    if order_type is None:
        return json_error_response("未注明订单类别，无法提交订单")
    if order_list is None:
        return json_error_response("订单内容不能为空，下单失败")

    order_list = json.loads(order_list)
    if len(order_list) < 1:
        return json_error_response("订单内容不能为空，下单失败")

    params = {}
    res = create_order(member_id, order_list, params=params)
    app.logger.debug("type of res: %s" % type(res))
    app.logger.debug("res error: %s" % str(res))

    if res["code"] == 200 and order_type == "cart":
        food_id_list = [item["food_id"] for item in order_list]
        delete_cart_info(member_id, food_id_list)

    return make_response(jsonify(res))

@api_blueprint.route("/order/pay", methods=["POST"])
def order_pay():
    if g.current_member is None:
        return json_error_response("请先登录再完成支付")
    if g.current_member.status != 1:
        return json_error_response("该账户已被注销，无法完成支付")
    member_info = g.current_member

    order_sn = request.form.get("order_sn", None)
    if order_sn is None:
        return json_error_response("支付失败，请稍后再试（1）")

    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if pay_order_info is None:
        return json_error_response("支付失败，请稍后再试（2）")

    # get openid for member
    oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_info.id).first()
    if oauth_bind_info is None:
        return json_error_response("支付失败，请稍后再试（3）")

    return json_response()