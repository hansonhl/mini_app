"""
$ python main.py run -m queue/index
"""
from application import app, db
from common.models.queue_list import QueueList
from common.models.pay_order import PayOrder
from common.models.pay_order_item import PayOrderItem
from common.libs.utils import get_current_time
import json

class Task():
    def __init__(self):
        pass

    def run(self, params):
        queue_list = QueueList.filter_by(status=-1).order_by(QueueList.id.asc()).limit(3).all()
        for item in queue_list:
            if item.queue_name == "pay":
                self.handle_pay(item)
            item.status = 1
            item.updated_time = get_current_time()
            db.session.add(item)

        db.session.commit()

    def handle_pay(self, item):
        data = json.loads(item.data)
        if "member_id" not in data or "pay_order_id" not in data:
            return False

        pay_order_info = PayOrder.query.filter_by(id=data["pay_order_id"]).first()
        if not pay_order_info:
            return False

        pass