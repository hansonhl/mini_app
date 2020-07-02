# coding: utf-8
from application import app, db

class Member(db.Model):
    __tablename__ = 'member'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='???')
    mobile = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue(), info='??????')
    sex = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?? 1?? 2??')
    avatar = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), info='????')
    salt = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='??salt')
    reg_ip = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='??ip')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?? 1??? 0???')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')

    @property
    def sex_desc(self):
        desc_list = ["未填写", "男", "女", "其他"]
        return desc_list[self.sex]

    @property
    def status_desc(self):
        return app.config["ACCOUNT_STATUS_MAPPING"][str(self.status)]