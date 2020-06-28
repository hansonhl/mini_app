from flask import Blueprint
from common.libs.utils import render_template_with_global_vars

food_blueprint = Blueprint("food", __name__)

@food_blueprint.route("/index")
def index():
    return render_template_with_global_vars("food/index.html")

@food_blueprint.route("/info")
def info():
    return render_template_with_global_vars("food/info.html")

@food_blueprint.route("/set")
def set():
    return render_template_with_global_vars("food/set.html")

@food_blueprint.route("/cat")
def cat():
    return render_template_with_global_vars("food/cat.html")

@food_blueprint.route("/cat_set")
def cat_set():
    return render_template_with_global_vars("food/cat_set.html")