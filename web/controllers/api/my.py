from flask import request, g, jsonify, make_response
from decimal import Decimal
import json

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, \
    get_id_to_model_dict, get_int, require_login, get_current_time
from common.libs.url_utils import build_image_url

from common.models.food import Food
from common.models.pay_order import PayOrder
from common.models.pay_order_item import PayOrderItem
from common.models.member_comments import MemberComment

from application import app, db

@api_blueprint.route("/my/order", methods=["POST"])
@require_login
def my_order():
    member_id = g.current_member.id

    status = get_int(request.form, "status", None)
    if status is None:
        return json_error_response("查询订单信息失败，请注明订单状态")

    pay_order_query = PayOrder.query.filter_by(member_id=member_id)

    if status == -8: #待付款
        pay_order_query = pay_order_query.filter(PayOrder.status == -8)
    elif status == -7: #待付款
        pay_order_query = pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == -7)
    elif status == -6: #待确认
        pay_order_query = pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == -6)
    elif status == -5: #待评价
        pay_order_query = pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == 1,
                               PayOrder.comment_status == 0)
    elif status == 1: #已完成
        pay_order_query = pay_order_query.filter(PayOrder.status == 1, PayOrder.deliver_status == 1,
                               PayOrder.comment_status == 1)
    elif status == 0: #未完成
        pay_order_query = pay_order_query.filter(PayOrder.status.in_([0, -1, -2, -9]))
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
            "order_sn": order.order_sn,
            "note": order.note,
            "total_price": str(order.total_price),
            "goods_list": oid_to_items[order.id]
        } for order in pay_order_list]

    data = {"pay_order_list": pay_order_data_list}
    return json_response(data=data)


@api_blueprint.route("/my/comment/add", methods=["POST"])
@require_login
def my_comment_add():
    member_id = g.current_member.id

    order_sn = request.form.get("order_sn", None)
    if not order_sn:
        return json_error_response("评价操作失败（1）")

    pay_order_info = PayOrder.query.filter_by(member_id=member_id, order_sn=order_sn).first()
    if not pay_order_info:
        return json_error_response("评价操作失败（2）")

    if pay_order_info.comment_status:
        return json_error_response("已经评价过了，请勿重复评价")

    pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
    food_ids = "_".join(str(item.food_id) for item in pay_order_items)

    score = get_int(request.form, "score", 10)
    content = request.form.get("content", "")

    comment_info = MemberComment()
    comment_info.member_id = member_id
    comment_info.food_ids = "_" + food_ids + "_"
    comment_info.pay_order_id = pay_order_info.id
    comment_info.score = score
    comment_info.content = content
    comment_info.created_time = get_current_time()

    db.session.add(comment_info)
    db.session.commit()

    pay_order_info.comment_status = 1
    pay_order_info.updated_time = get_current_time()
    db.session.add(pay_order_info)
    db.session.commit()

    return json_response()

@api_blueprint.route("/my/comment/list", methods=["GET"])
@require_login
def my_comment_list():
    member_id = g.current_member.id

    comment_order_list = db.session.query(MemberComment, PayOrder)\
        .filter(MemberComment.pay_order_id == PayOrder.id).all()
    res_list = [{
        "date": str(comment.created_time),
        "order_number": pay_order.order_number,
        "content": comment.content
    } for comment, pay_order in comment_order_list]

    return json_response(data={"list": res_list})