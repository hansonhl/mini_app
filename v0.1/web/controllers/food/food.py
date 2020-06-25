from flask import Blueprint, render_template

food_blueprint = Blueprint("food", __name__)

@food_blueprint.route("/index")
def index():
    return render_template("food/index.html")

@food_blueprint.route("/info")
def info():
    return render_template("food/info.html")

@food_blueprint.route("/set")
def set():
    return render_template("food/set.html")

@food_blueprint.route("/cat")
def cat():
    return render_template("food/cat.html")

@food_blueprint.route("/cat_set")
def cat_set():
    return render_template("food/cat_set.html")