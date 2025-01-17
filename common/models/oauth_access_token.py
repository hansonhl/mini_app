# coding: utf-8
from application import db

class OauthAccessToken(db.Model):
    __tablename__ = 'oauth_access_token'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(600), nullable=False, server_default=db.FetchedValue())
    expired_time = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
