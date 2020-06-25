from flask import Blueprint, render_template

finance_blueprint = Blueprint("finance", __name__)

@finance_blueprint.route("/index")
def index():
    return render_template("finance/index.html")

@finance_blueprint.route("/account")
def account():
    return render_template("finance/account.html")

@finance_blueprint.route("/pay_info")
def pay_info():
    return render_template("finance/pay_info.html")
