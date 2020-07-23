from common.models.pay_order import PayOrder
import common.libs.pay_utils as pay_utils
import json, requests, datetime

from application import app

"""
$ python main.py run -m pay/index
"""
class Task():
    def __init__(self):
        pass

    def run(self, params):
        time_now = datetime.datetime.now()
        time_30_mins_before = time_now + datetime.timedelta(minutes=-30)

        cancel_list = PayOrder.query.filter_by(status=-8)\
            .filter(PayOrder.created_time <= time_30_mins_before.strftime("%Y-%m-%d %H:%M:%S")) \
            .all()

        if not cancel_list:
            app.logger.info("No pay orders were cancelled")
            return

        for item in cancel_list:
            pay_utils.close_order(item.id)

        app.logger.info("Cancelled %d pay orders due to inactivity" % len(cancel_list))