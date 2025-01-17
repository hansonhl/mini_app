# coding: utf-8
from application import db

class User(db.Model):
    __tablename__ = 'user'

    uid = db.Column(db.BigInteger, primary_key=True, info='??uid')
    nickname = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='???')
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='????')
    email = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='????')
    gender = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1?? 2?? 3: ?? 0????')
    avatar = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='??')
    login_name = db.Column(db.String(20), nullable=False, unique=True, server_default=db.FetchedValue(), info='?????')
    login_pwd = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='????')
    login_salt = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='???????????')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1??? 0???')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
