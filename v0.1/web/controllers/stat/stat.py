from flask import Blueprint, render_template

stat_blueprint = Blueprint("stat", __name__)

@stat_blueprint.route("/index")
def index():
    return render_template("stat/index.html")

@stat_blueprint.route("/food")
def food():
    return render_template("stat/food.html")

@stat_blueprint.route("/member")
def member():
    return render_template("stat/member.html")

@stat_blueprint.route("/share")
def share():
    return render_template("stat/share.html")