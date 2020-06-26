from flask import Blueprint, render_template

from common.libs.utils import render_template_with_global_vars

index_blueprint = Blueprint("index", __name__)

@index_blueprint.route("/")
def index():
    return render_template_with_global_vars("index/index.html")

@index_blueprint.route("/api")
def api():
    return "Hello"
