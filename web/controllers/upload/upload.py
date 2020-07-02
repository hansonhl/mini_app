import json
from flask import Blueprint, request, make_response, jsonify
from common.libs.utils import json_error_response, json_response

from application import app

upload_blueprint = Blueprint("upload", __name__)

@upload_blueprint.route("/ueditor", methods=["GET", "POST"])
def ueditor():
    action = request.args.get("action", None)
    if action == "config":
        config_data = {}
        config_path = "%s/web/static/plugins/ueditor/upload_config.json" % app.root_path
        with open(config_path, "r") as f:
            config_data = json.load(f)
        return make_response(jsonify(config_data))
    return "upload"