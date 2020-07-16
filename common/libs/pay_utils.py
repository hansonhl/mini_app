from decimal import Decimal
from application import app, db
import hashlib, time, random

from common.libs.utils import get_current_time
from common.libs.food_utils import set_food_stock_change_log

from common.models.food import Food
from common.models.food_sale_change_log import FoodSaleChangeLog
from common.models.pay_order import PayOrder
from common.models.pay_order_item import PayOrderItem
from common.models.pay_order_callback_data import PayOrderCallbackData


def create_order(member_id, items, params=None):
    res = {"code": -1, "msg": "", "data": {}}
    for item in items:
        item["price"] = Decimal(item["price"])
    food_id_list = [item["food_id"] for item in items if item["price"] >= 0]

    pay_price = Decimal(sum(item["price"] * item["quantity"]
                            for item in items if item["price"] >= 0))

    if len(food_id_list) <= 0:
        res["msg"] = "订购商品列表为空，或者所有商品的价格都小于等于0元"
        return res

    deliver_price = Decimal(params.get("deliver_price", 0))
    notes = params.get("note", "")
    total_price = pay_price + deliver_price

    # concurrent handling of orders. We use a pessimistic row-level lock, where
    # a lock is held by a thread/process even when they are just querying the value
    try:
        food_info_list = db.session.query(Food).filter(Food.id.in_(food_id_list)) \
            .with_for_update().all()
        food_id_to_stock_map = {food.id: food.stock for food in food_info_list}

        pay_order = PayOrder()
        pay_order.order_sn = generate_order_sn()
        pay_order.member_id = member_id
        pay_order.total_price = total_price
        pay_order.deliver_price = deliver_price
        pay_order.pay_price = pay_price
        pay_order.note = notes
        pay_order.status = -8
        pay_order.deliver_status = -8
        pay_order.updated_time = pay_order.created_time = get_current_time()
        db.session.add(pay_order)

        for item in items:
            food_id = item["food_id"]
            quantity = item["quantity"]
            price = item["price"]
            stock = food_id_to_stock_map[food_id]
            if price < 0:
                continue
            if quantity > stock:
                raise Exception("您购买的菜品数量太火爆了，剩余%d, 您购买了%d" % (stock, quantity))

            update_successful = Food.query.filter_by(id=food_id).update({
                "stock": stock - quantity
            })

            if not update_successful:
                raise Exception("下单失败，请重新下单 （1）")
            if not set_food_stock_change_log(food_id, stock, -1 * quantity, "由用户%d下单购买" % member_id):
                raise Exception("下单失败，请重新下单 （2）")

            pay_order_item = PayOrderItem()
            pay_order_item.pay_order_id = pay_order.id
            pay_order_item.member_id = member_id
            pay_order_item.quantity = quantity
            pay_order_item.price = price
            pay_order_item.food_id = food_id
            pay_order_item.note = notes
            pay_order_item.created_time = pay_order_item.updated_time = get_current_time()

            db.session.add(pay_order_item)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        res["msg"] = str(e)
        return res

    res["code"] = 200
    res["msg"] = "下单成功！"
    res["data"] = {
        "pay_order_id": pay_order.id,
        "order_sn": pay_order.order_sn,
        "total_price": str(pay_order.total_price)
    }
    return res

def order_success(pay_order_id=0, pay_sn=""):
    # pessimistic concurrent handling:
    try:
        pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()
        if pay_order_info is None or pay_order_info.status not in [-8, -7]:
            return True

        pay_order_info.pay_sn = pay_sn
        pay_order_info.status = 1
        pay_order_info.deliver_status = -7
        pay_order_info.pay_time = get_current_time()
        pay_order_info.updated_time = get_current_time()
        db.session.add(pay_order_info)

        # update FoodSaleChangeLog
        pay_order_items = PayOrderItem.filter_by(pay_order_id=pay_order_id).all()
        for order_item in pay_order_items:
            sale_log = FoodSaleChangeLog()
            sale_log.food_id = order_item.food_id
            sale_log.quantity = order_item.quantity
            sale_log.price = order_item.price
            sale_log.member_id = order_item.member_id
            sale_log.created_time = get_current_time()
            db.session.add(sale_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return False

    return True

def add_pay_callback_data( pay_order_id=0, type="pay", data=""):
    cb_info = PayOrderCallbackData()
    cb_info.pay_order_id = pay_order_id
    if type == "pay":
        cb_info.pay_data = data
        cb_info.refund_data = ""
    else:
        cb_info.pay_data = ""
        cb_info.refund_data = data

    cb_info.created_time = cb_info.updated_time = get_current_time()
    db.session.add(cb_info)
    db.session.commit()
    return True

def generate_order_sn():
    m = hashlib.md5()
    sn = None
    while True:
        s = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 999999))
        m.update(s.encode("utf-8"))
        sn = m.hexdigest()
        if not PayOrder.query.filter_by(order_sn=sn).first():
            return sn
