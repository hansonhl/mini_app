from application import app

from flask import Blueprint, render_template

index_blueprint = Blueprint("index", __name__)

@index_blueprint.route("/")
def index():
    return render_template("index/index.html")

@index_blueprint.route("/api")
def api():
    return "Hello"
