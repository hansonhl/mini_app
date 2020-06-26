from flask import Blueprint
from common.libs.utils import render_template_with_global_vars

stat_blueprint = Blueprint("stat", __name__)

@stat_blueprint.route("/index")
def index():
    return render_template_with_global_vars("stat/index.html")

@stat_blueprint.route("/food")
def food():
    return render_template_with_global_vars("stat/food.html")

@stat_blueprint.route("/member")
def member():
    return render_template_with_global_vars("stat/member.html")

@stat_blueprint.route("/share")
def share():
    return render_template_with_global_vars("stat/share.html")