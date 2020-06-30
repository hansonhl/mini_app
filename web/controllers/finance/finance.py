from flask import Blueprint
from common.libs.utils import render_template_with_global_vars

finance_blueprint = Blueprint("finance", __name__)

@finance_blueprint.route("/index")
def index():
    return render_template_with_global_vars("finance/index.html")

@finance_blueprint.route("/account")
def account():
    return render_template_with_global_vars("finance/account.html")

@finance_blueprint.route("/pay_info")
def pay_info():
    return render_template_with_global_vars("finance/pay_info.html")
