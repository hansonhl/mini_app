"""
$ python main.py run -m queue/index
"""
from application import app, db
from common.models.queue_list import QueueList
from common.models.pay_order import PayOrder
from common.models.pay_order_item import PayOrderItem
from common.models.oauth_member_bind import OauthMemberBind
from common.models.food import Food

from common.libs.utils import get_current_time
import common.libs.wechat_utils as wc_utils

import json, requests

class Task():
    def __init__(self):
        pass

    def run(self, params):
        queue_list = QueueList.query.filter_by(status=-1).order_by(QueueList.id.asc()).limit(3).all()
        for item in queue_list:
            if item.queue_name == "pay":
                self.handle_pay(item)
            item.status = 1
            item.updated_time = get_current_time()
            db.session.add(item)

        db.session.commit()

    def handle_pay(self, item):
        """ 发送订阅消息 """
        data = json.loads(item.data)
        if "member_id" not in data or "pay_order_id" not in data:
            app.logger.error("member_id or pay_order_id not provided!")
            return False

        oauth_member_bind_info = OauthMemberBind.query.filter_by(member_id=data["member_id"]).first()
        if not oauth_member_bind_info:
            app.logger.error("oauth_member_bind_info not found, member_id may be invalid")
            return False
        openid = oauth_member_bind_info.openid

        pay_order_info = PayOrder.query.filter_by(id=data["pay_order_id"]).first()
        if not pay_order_info:
            app.logger.error("pay_order_info not found, pay_order_id may be invalid")
            return False

        if not pay_order_info.subscribed:
            app.logger.info("This user has not subscribed, subscribe message will not be sent")
            return False

        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
        food_item_msgs = []
        if pay_order_items:
            for item in pay_order_items:
                food_info = Food.query.filter_by(id=item.food_id).first()
                if not food_info:
                    continue
                food_item_msgs.append("%s %s份" % (food_info.name, item.quantity))

        amount1 = str(pay_order_info.total_price)
        date2 = pay_order_info.updated_time.strftime("%Y-%m-%d %H:%M:%S")
        note3 = pay_order_info.note
        note3 = "（无）" if len(note3) == 0 else note3
        items4 = "、".join(food_item_msgs)
        order_sn5 = pay_order_info.order_sn

        access_token = wc_utils.get_access_token()
        url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token=%s" % access_token
        params = {
            "touser": openid,
            "template_id": "7--0oU7_LN9YjbGFUmRnLDpfikYeC09tpcVnRPffZHY",
            "page": "/my/order_list",
            "miniprogram_state":"developer",
            "lang":"zh_CN",
            "data": {
                "amount1": {
                  "value": amount1
                },
                "date2": {
                  "value": date2
                },
                "thing3": {
                  "value": note3
                },
                "thing4": {
                  "value": items4
                },
                "character_string5": {
                    "value": order_sn5
                }
            }
        }

        headers = {"Content-Type": "application/json"}
        r = requests.post(url=url,data=json.dumps(params), headers=headers)
        r.encoding = "utf-8"
        app.logger.info(r.text)
        return True
