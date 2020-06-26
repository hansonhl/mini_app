from flask import Blueprint
from common.libs.utils import render_template_with_global_vars


member_blueprint = Blueprint("member", __name__)

@member_blueprint.route("/index")
def index():
    return render_template_with_global_vars("member/index.html")

@member_blueprint.route("/info")
def info():
    return render_template_with_global_vars("member/info.html")

@member_blueprint.route("/set")
def set():
    return render_template_with_global_vars("member/set.html")

@member_blueprint.route("/comment")
def comment():
    return render_template_with_global_vars("member/comment.html")