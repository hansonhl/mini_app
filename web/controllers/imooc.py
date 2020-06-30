from flask import Blueprint

route_imooc = Blueprint("imooc_page", __name__)

@route_imooc.route("/")
def index():
    return "imooc index page"

@route_imooc.route("/hello")
def hello():
    return "Hi again"