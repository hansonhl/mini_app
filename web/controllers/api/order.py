from flask import request, g, jsonify, make_response
from decimal import Decimal
import json

from web.controllers.api import api_blueprint
from common.libs.utils import json_response, json_error_response, \
    get_current_time, require_login, get_int
from common.libs.url_utils import build_image_url, build_url
from common.libs.cart_utils import delete_cart_info

import common.libs.pay_utils as pay_utils
import common.libs.wechat_utils as wc_utils

from common.models.food import Food
from common.models.pay_order import PayOrder
from common.models.oauth_member_bind import OauthMemberBind
from common.models.member_address import MemberAddress

from application import app, db
from decimal import Decimal

@api_blueprint.route("/order/info", methods=["POST"])
@require_login
def order_info():
    member_id = g.current_member.id

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

    default_address = {}
    default_addr_info = MemberAddress.query.filter_by(status=1, is_default=1, member_id=member_id).first()
    if default_addr_info:
        default_address = {
            "id": default_addr_info.id,
            "name": default_addr_info.contact_name,
            "mobile": default_addr_info.mobile,
            "address": "%s%s%s%s" % (default_addr_info.province_str,
                                     default_addr_info.city_str,
                                     default_addr_info.district_str,
                                     default_addr_info.address)
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
@require_login
def order_create():
    member_id = g.current_member.id

    order_type = request.form.get("type", None)
    order_list = request.form.get("purchaseList", None)
    address_id = get_int(request.form, "address_id", 0)
    deliver_price = Decimal(request.form.get("deliver_price", "0.00"))
    note = request.form.get("note", "")

    if order_type is None:
        return json_error_response("未注明订单类别，无法提交订单")
    if order_list is None:
        return json_error_response("订单内容不能为空，下单失败")
    if address_id is None:
        return json_error_response("未填写地址")

    order_list = json.loads(order_list)
    if len(order_list) < 1:
        return json_error_response("订单内容不能为空，下单失败")

    address_info = MemberAddress.query.filter_by(id=address_id).first()
    if not address_info or address_info.status != 1:
        return json_error_response("未填写地址，或者地址信息有误")


    params = {
        "shipping_price": deliver_price,
        "note": note,
        "deliver_address_id": address_info.id,
        "deliver_info": {
            "name": address_info.contact_name,
            "mobile": address_info.mobile,
            "address": "%s%s%s%s" % (address_info.province_str,
                                     address_info.city_str,
                                     address_info.district_str,
                                     address_info.address)
        }
    }
    res = pay_utils.create_order(member_id, order_list, params=params)
    app.logger.debug("type of res: %s" % type(res))
    app.logger.debug("res error: %s" % str(res))

    if res["code"] == 200 and order_type == "cart":
        food_id_list = [item["food_id"] for item in order_list]
        delete_cart_info(member_id, food_id_list)

    return make_response(jsonify(res))

@api_blueprint.route("/order/pay", methods=["POST"])
@require_login
def order_pay():
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

    subscribed = request.form.get("subscribed", "False")
    subscribed = subscribed == "true"

    notify_url = build_url("/api/order/callback")
    data = {
        "appid": app.config["MINA_APP_ID"],
        "mch_id": app.config["MCH_ID"],
        "nonce_str": wc_utils.get_nonce_str(),
        "body": "订餐",
        "out_trade_no": pay_order_info.order_sn,
        "total_fee": int(pay_order_info.total_price * 100), #单位为分
        "notify_url": notify_url,
        "trade_type": "JSAPI",
        "openid": oauth_bind_info.openid
    }
    prepay_info = wc_utils.get_pay_info(data)
    # save prepay_id to database
    pay_order_info.prepay_id = prepay_info["prepay_id"]
    pay_order_info.subscribed = subscribed
    db.session.add(pay_order_info)
    db.session.commit()

    res_data = {"prepay_info":prepay_info}

    if app.config["DEV_MODE"]:
        # prepare callback xml message right here, send to frontend, and then
        # frontend will send it back to backend's /order/callback_dev
        res_data["dev_mode"] = True
        cb_dev_data = {
            "appid": data["appid"],
            "bank_type": "CFT",
            "cash_fee": data["total_fee"],
            "fee_type": "CNY",
            "is_subscribe": "N",
            "mch_id": app.config["MCH_ID"],
            "nonce_str": wc_utils.get_nonce_str(),
            "openid": oauth_bind_info.openid,
            "out_trade_no": pay_order_info.order_sn,
            "result_code": "SUCCESS",
            "return_code": "SUCCESS",
            "time_end": get_current_time("%Y%m%d%H%M%S"),
            "total_fee": data["total_fee"],
            "trade_type": "JSAPI",
            # this is supposed to be automatically generated by WeChat API
            # use our own order_sn temporarily for development purposes
            "transaction_id": pay_order_info.order_sn
        }
        sign = wc_utils.create_sign(cb_dev_data)
        cb_dev_data["sign"] = sign
        xml_data = wc_utils.dict_to_xml(cb_dev_data)
        res_data["cb_dev_data"] = xml_data

    return json_response(data=res_data)


@api_blueprint.route("/order/callback", methods=["POST"])
@require_login
def order_callback():
    """ 支付结果通知
    <xml>
    <appid></appid>
    <bank_type>CFT</bank_type>
    <cash_fee>1</cash_fee>
    <fee_type>CNY</fee_type>
    <is_subscribe>N</is_subscribe>
    <mch_id></mch_id>
    <nonce_str></nonce_str>
    <openid></openid>
    <out_trade_no></out_trade_no>
    <result_code>SUCCESS</result_code>
    <return_code>SUCCESS</return_code>
    <sign></sign>
    <time_end></time_end>
    <total_fee>1</total_fee>
    <trade_type>JSAPI</trade_type>
    <transaction_id></transaction_id>
    </xml>
    """
    fail_res = {"return_code": "FAIL", "return_msg": "FAIL"}
    header = {"Content-Type": "application/xml"}
    callback_data = wc_utils.xml_to_dict(request.data)
    sign = callback_data["sign"]
    callback_data.pop("sign")
    check_sign = wc_utils.create_sign(callback_data)
    if sign != check_sign:
        return wc_utils.dict_to_xml(fail_res), header

    order_sn = callback_data["out_trade_no"]
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()

    if pay_order_info is None:
        return wc_utils.dict_to_xml(fail_res), header

    if int(pay_order_info.total_price * 100) != int(callback_data["total_fee"]):
        return wc_utils.dict_to_xml(fail_res), header

    success_res = {"return_code": "SUCCESS", "return_msg": "OK"}
    if pay_order_info.status == 1:
        return wc_utils.dict_to_xml(success_res), header

    # callback succeeded, modify records and states in database
    pay_sn = callback_data["transaction_id"]
    pay_utils.order_success(pay_order_id=pay_order_info.id, pay_sn=pay_sn)

    # add record of this successful transaction to database
    pay_utils.add_pay_callback_data(pay_order_id=pay_order_info.id,
                                    data=request.data) # pass raw form of data

    return wc_utils.dict_to_xml(success_res), header


@api_blueprint.route("/order/callback_dev", methods=["POST"])
def order_callback_dev():
    """ Dev mode handling """
    if not app.config["DEV_MODE"]:
        return json_error_response("操作有误！")

    xml_data = request.form.get("xml", None)

    callback_data = wc_utils.xml_to_dict(xml_data)

    sign = callback_data.pop("sign")
    check_sign = wc_utils.create_sign(callback_data)
    if sign != check_sign:
        return json_error_response("操作有误（1）")

    order_sn = callback_data["out_trade_no"]
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()

    if pay_order_info is None:
        return json_error_response("操作有误（2）")

    if int(pay_order_info.total_price * 100) != int(callback_data["total_fee"]):
        return json_error_response("操作有误（3）")

    if pay_order_info.status == 1:
        return json_error_response("操作有误（4）")

    # callback succeeded, modify records and states in database
    # tables affected: PayOrder, PayOrderCallbackData, FoodSaleChangeLog
    pay_sn = callback_data["transaction_id"]

    res = pay_utils.order_success(pay_order_id=pay_order_info.id, pay_sn=pay_sn)
    if not res:
        return json_error_response("操作有误（5）")

    # add record of this successful transaction to database
    pay_utils.add_pay_callback_data(pay_order_id=pay_order_info.id,
                                    data=xml_data)  # pass raw form of data

    return json_response("【开发模式】付款成功，信息已录入数据库")

@api_blueprint.route("/order/ops", methods=["POST"])
@require_login
def order_ops():
    member_info = g.current_member

    order_sn = request.form.get("order_sn", None)
    if order_sn is None:
        return json_error_response("订单操作失败（1）")

    action = request.form.get("action", None)
    if action is None:
        return json_error_response("订单操作失败（2）")

    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if pay_order_info is None:
        return json_error_response("订单操作失败（3）")

    if action == "cancel":
         if pay_utils.close_order(pay_order_id=pay_order_info.id):
             return json_response("取消订单成功")
         else:
             return json_error_response("订单操作失败（4）")

    elif action == "confirm":
        pay_order_info.deliver_status = 1
        pay_order_info.updated_time = get_current_time()
        db.session.add(pay_order_info)
        db.session.commit()
        return json_response("确认收货成功")
    elif action == "comment":
        pass
    else:
        return json_response("订单操作失败（5）")

