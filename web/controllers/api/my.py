from flask import request, g, jsonify, make_response
from decimal import Decimal
import json

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, get_id_to_model_dict, get_int
from common.libs.url_utils import build_image_url
from common.libs.cart_utils import delete_cart_info
from common.libs.pay_utils import create_order

from common.models.food import Food
from common.models.pay_order import PayOrder
from common.models.pay_order_item import PayOrderItem

from application import app, db

@api_blueprint.route("/my/order", methods=["POST"])
def my_order():
    if g.current_member is None:
        return json_error_response("请先登录再查询订单信息")
    if g.current_member.status != 1:
        return json_error_response("该账户已被注销，无法查询订单信息")
    member_id = g.current_member.id

    status = get_int(request.form, "status", None)
    if status is None:
        return json_error_response("查询订单信息失败，请注明订单状态")

    pay_order_query = PayOrder.query.filter_by(member_id=member_id)

    if status == -8: #待付款
        pay_order_query.filter(PayOrder.status == -8)
    elif status == -7: #待发货
        pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == -7)
    elif status == -6: #待确认
        pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == -6)
    elif status == -5: #待评价
        pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == 1,
                               PayOrder.comment_status == 0)
    elif status == 1: #已完成
        pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == 1,
                               PayOrder.comment_status == 1)
    elif status == 0: #未完成
        pay_order_query.filter(PayOrder.status.in_([0, -1, -2, -9]))
    else:
        return json_error_response("查询订单信息失败，订单状态有误")

    pay_order_list = pay_order_query.order_by(PayOrder.id.desc()).all()
    pay_order_data_list = []
    if pay_order_list:
        pay_order_ids = [pay_order.id for pay_order in pay_order_list]
        pay_order_items_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids))
        food_ids = [item.food_id for item in pay_order_items_list]
        fid_to_info = get_id_to_model_dict(Food, "id", Food.id, food_ids)

        oid_to_items = {}
        for item in pay_order_items_list:
            oid = item.pay_order_id
            fid = item.food_id
            if oid not in oid_to_items:
                oid_to_items[oid] = []
            food_info = fid_to_info[fid]
            oid_to_items[oid].append({
                "pay_order_item_id": item.id,
                "food_id": fid,
                "quantity": item.quantity,
                "pic_url": build_image_url(food_info.main_image),
                "name": food_info.name
            })

        pay_order_data_list = [{
            "status": order.pay_status,
            "status_desc": order.pay_status_desc,
            "date": order.created_time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_number": order.order_number,
            "note": order.note,
            "total_price": str(order.total_price),
            "goods_list": oid_to_items[order.id]
        } for order in pay_order_list]

    data = {"pay_order_list": pay_order_data_list}
    return json_response(data=data)