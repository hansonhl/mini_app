from flask import Blueprint, render_template

member_blueprint = Blueprint("member", __name__)

@member_blueprint.route("/index")
def index():
    return render_template("member/index.html")

@member_blueprint.route("/info")
def info():
    return render_template("member/info.html")

@member_blueprint.route("/set")
def set():
    return render_template("member/set.html")

@member_blueprint.route("/comment")
def comment():
    return render_template("member/comment.html")