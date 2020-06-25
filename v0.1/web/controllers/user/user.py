from flask import Blueprint, render_template

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/login")
def login():
    return render_template("user/login.html")

@user_blueprint.route("/edit")
def edit():
    return render_template("user/edit.html")

@user_blueprint.route("/reset-pwd")
def reset_pwd():
    return render_template("user/reset_pwd.html")