from flask import Blueprint
from common.libs.utils import render_template_with_global_vars

account_blueprint = Blueprint("account", __name__)

@account_blueprint.route("/index")
def index():
    return render_template_with_global_vars("account/index.html")

@account_blueprint.route("/info")
def info():
    return render_template_with_global_vars("account/info.html")

@account_blueprint.route("/set")
def set():
    return render_template_with_global_vars("account/set.html")