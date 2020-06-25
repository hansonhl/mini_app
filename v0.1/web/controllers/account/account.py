from flask import Blueprint, render_template

account_bluprint = Blueprint("account", __name__)

@account_bluprint.route("/index")
def index():
    return render_template("account/index.html")

@account_bluprint.route("/info")
def info():
    return render_template("account/info.html")

@account_bluprint.route("/set")
def set():
    return render_template("account/set.html")