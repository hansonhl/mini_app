# coding: utf-8
from application import db
class AppErrorLog(db.Model):
    __tablename__ = 'app_error_log'

    id = db.Column(db.Integer, primary_key=True)
    referer_url = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='?????refer')
    target_url = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='???url')
    query_params = db.Column(db.Text, nullable=False, info='get?post??')
    content = db.Column(db.String, nullable=False, info='????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
