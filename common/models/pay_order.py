# coding: utf-8
from application import app, db
class PayOrder(db.Model):
    __tablename__ = 'pay_order'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_sn = db.Column(db.String(40), nullable=False, unique=True, server_default=db.FetchedValue(), info='?????')
    member_id = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='??id')
    total_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='??????')
    shipping_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='????')
    base_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='??????')
    pay_sn = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='??????')
    prepay_id = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='?????id')
    note = db.Column(db.Text, nullable=False, info='????')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1????? 0 ?? -1 ???? -2 ??? -9 ????  -8 ???  -7 ???????')
    deliver_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?????-8 ??? -7 ?????? 1????? 0???')
    deliver_address_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='????id')
    deliver_info = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), info='????')
    comment_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='????')
    subscribed = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='????????')
    pay_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='??????')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')

    @property
    def pay_status(self):
        res = self.status
        if self.status == 1:
            res = self.deliver_status
            if self.deliver_status == 1 and self.comment_status == 0:
                res = -5
            if self.deliver_status == 1 and self.comment_status == 1:
                res = 1
        return res

    @property
    def pay_status_desc(self):
        return app.config["PAY_STATUS_MAPPING"][str(self.pay_status)]

    @property
    def order_number(self):
        # zfill() fills in zeros on the left size to 5 digits.
        return self.created_time.strftime("%Y%m%d%H%M%S") + str(self.id).zfill(
            5)
