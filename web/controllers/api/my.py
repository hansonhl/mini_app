from flask import request, g, jsonify, make_response
import datetime, json

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, require_login
from common.libs import utils
from common.libs.url_utils import build_image_url

from common.models.food import Food
from common.models.pay_order import PayOrder
from common.models.pay_order_item import PayOrderItem
from common.models.member_comments import MemberComment
from common.models.member_address import MemberAddress

from application import app, db

@api_blueprint.route("/my/index", methods=["GET"])
@require_login
def my_index():
    data = {"user_info": {
        "avatar_url": g.current_member.avatar,
        "nickname": g.current_member.nickname,
        "mobile": g.current_member.mobile
    }}
    return json_response(data=data)

@api_blueprint.route("/my/order", methods=["POST"])
@require_login
def my_order():
    member_id = g.current_member.id

    status = utils.get_int(request.form, "status", None)
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

    # TODO: use table join method to retrieve data
    pay_order_list = pay_order_query.order_by(PayOrder.id.desc()).all()
    pay_order_data_list = []
    if pay_order_list:
        pay_order_ids = [pay_order.id for pay_order in pay_order_list]
        pay_order_items_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids))
        food_ids = [item.food_id for item in pay_order_items_list]
        fid_to_info = utils.get_id_to_model_dict(Food, "id", Food.id, food_ids)

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

@api_blueprint.route("/my/order/info", methods=["GET"])
@require_login
def my_order_info():
    order_sn = request.values.get("order_sn", "")
    if not order_sn:
        return json_error_response("查询订单信息错误，请稍后再试（1）")

    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        return json_error_response("查询订单信息错误，请稍后再试（2）")

    pay_wait_time = app.config["PAY_WAIT_TIME"]
    deadline = pay_order_info.created_time + datetime.timedelta(minutes=pay_wait_time)
    address_info = json.loads(pay_order_info.deliver_info)
    data = {
        "order_sn": pay_order_info.order_sn,
        "status": pay_order_info.pay_status,
        "status_desc": pay_order_info.pay_status_desc,
        "deadline": deadline.strftime("%Y-%m-%d %H:%M"),
        "address": address_info,
        "base_price": str(pay_order_info.base_price),
        "shipping_price": str(pay_order_info.shipping_price),
        "total_price": str(pay_order_info.total_price),
    }

    # "poi" short for "PayOrderItem"
    poi_and_food_list = db.session.query(PayOrderItem, Food).filter(
        PayOrderItem.pay_order_id == pay_order_info.id,
        PayOrderItem.food_id == Food.id
    )

    goods = [{
        "pic_url": build_image_url(food.main_image),
        "name": food.name,
        "price": str(poi.price),
        "unit": poi.quantity
    } for poi, food in poi_and_food_list]

    data["goods"] = goods

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

    score = utils.get_int(request.form, "score", 10)
    content = request.form.get("content", "")

    comment_info = MemberComment()
    comment_info.member_id = member_id
    comment_info.food_ids = "_" + food_ids + "_"
    comment_info.pay_order_id = pay_order_info.id
    comment_info.score = score
    comment_info.content = content
    comment_info.created_time = utils.get_current_time()

    db.session.add(comment_info)
    db.session.commit()

    pay_order_info.comment_status = 1
    pay_order_info.updated_time = utils.get_current_time()
    db.session.add(pay_order_info)
    db.session.commit()

    return json_response()

@api_blueprint.route("/my/comment/list", methods=["GET"])
@require_login
def my_comment_list():
    member_id = g.current_member.id

    comment_order_list = db.session.query(MemberComment, PayOrder)\
        .filter(MemberComment.pay_order_id == PayOrder.id,
                MemberComment.member_id == member_id).all()
    res_list = [{
        "date": str(comment.created_time),
        "order_number": pay_order.order_number,
        "content": comment.content
    } for comment, pay_order in comment_order_list]

    return json_response(data={"list": res_list})


@api_blueprint.route("/my/address/get", methods=["GET"])
@require_login
def my_address_get():
    address_id = utils.get_int(request.values, "id", 0)
    address_info = MemberAddress.query.filter_by(id=address_id).first()
    if not address_info:
        return json_error_response("无法获取地址信息")

    prov_idx, city_idx, distr_idx = \
        utils.get_addr_idxs(address_info.province_id, address_info.city_id,
                            address_info.district_id)

    data = {
        "contact_name": address_info.contact_name,
        "mobile": address_info.mobile,
        "province_name": address_info.province_str,
        "city_name": address_info.city_str,
        "district_name": address_info.district_str,
        "province_idx": prov_idx,
        "city_idx": city_idx,
        "distr_idx": distr_idx,
        "address": address_info.address
    }
    return json_response(data=data)


@api_blueprint.route("/my/address/set", methods=["POST"])
@require_login
def my_address_set():
    member_id = g.current_member.id

    addr_id = utils.get_int(request.form, "id", 0)
    contact_name = request.form.get("contact_name", "")
    mobile = request.form.get("mobile", "")
    address = request.form.get("address", "")

    province_id = utils.get_int(request.form, "province_id", 0)
    city_id = utils.get_int(request.form, "city_id", 0)
    district_id = utils.get_int(request.form, "district_id", 0)

    province_str = request.form.get("province_str", "")
    city_str = request.form.get("city_str", "")
    district_str = request.form.get("district_str", "")

    empty_items = []
    for var, item in zip([contact_name, mobile, address, province_str, city_str, province_id, city_id],
                         ["联系人姓名", "手机号码", "详细地址", "省份名称", "城市名称", "省份代码", "城市代码"]):
        if not var:
            empty_items.append(item)
    if len(empty_items) > 0:
        return json_error_response("设置地址时以下内容不能为空：" + "、".join(empty_items))



    # check if addr_info already exists
    addr_info = MemberAddress.query.filter_by(id=addr_id).first()

    if addr_info:
        if addr_info.member_id != member_id:
            return json_error_response("修改地址时出现错误（1）")
    if not addr_info:
        default_addr_cnt = MemberAddress.query.filter_by(is_default=1,
                                                         member_id=member_id,
                                                         status=1).count()
        addr_info = MemberAddress()
        addr_info.member_id = member_id
        addr_info.is_default = 1 if default_addr_cnt == 0 else 0
        addr_info.created_time = utils.get_current_time()

    addr_info.contact_name = contact_name
    addr_info.mobile = mobile
    addr_info.province_id = province_id
    addr_info.province_str = province_str
    addr_info.city_id = city_id
    addr_info.city_str = city_str
    addr_info.district_id = district_id
    addr_info.district_str = district_str
    addr_info.address = address
    addr_info.updated_time = utils.get_current_time()

    db.session.add(addr_info)
    db.session.commit()

    return json_response("操作成功")

@api_blueprint.route("/my/address/list", methods=["GET"])
@require_login
def my_address_list():
    member_id = g.current_member.id
    address_info = MemberAddress.query.filter_by(member_id=member_id, status=1)
    address_list = [{
        "id": addr.id,
        "isDefault": addr.is_default == 1,
        "name": addr.contact_name,
        "mobile": addr.mobile,
        "address": "%s%s%s%s" % (addr.province_str, addr.city_str,
                                 addr.district_str, addr.address)
    } for addr in address_info]
    data = {"address_list": address_list}
    return json_response(data=data)

@api_blueprint.route("/my/address/ops", methods=["POST"])
@require_login
def my_address_ops():
    addr_id = utils.get_int(request.form, "id", 0)
    action = request.form.get("action", "")

    addr_info = MemberAddress.query.filter_by(id=addr_id).first()
    if not addr_info:
        return json_error_response("地址更改操作错误（1）")

    if action == "set_default":
        member_id = g.current_member.id
        current_time = utils.get_current_time()
        MemberAddress.query.filter_by(member_id=member_id) \
            .update({"is_default": 0, "updated_time": current_time})

        addr_info.is_default = 1
        addr_info.updated_time = utils.get_current_time()
        db.session.add(addr_info)
        db.session.commit()

        return json_response()
    elif action == "delete":
        addr_info.status = 0
        addr_info.updated_time = utils.get_current_time()
        db.session.add(addr_info)
        db.session.commit()

        latest_addr = MemberAddress.query.filter_by(status=1).order_by(MemberAddress.updated_time.desc()).first()
        if latest_addr:
            latest_addr.is_default = 1
            db.session.add(latest_addr)
            db.session.commit()

        return json_response()
    else:
        return json_error_response("地址更改操作错误（2）")