import json
from flask import Blueprint, request, make_response, jsonify
from common.libs.utils import json_error_response, json_response
from common.libs.upload_utils import upload_by_file
from common.libs.url_utils import build_image_url
from common.models.images import Image

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
    elif action == "uploadimage":
        return upload_image()
    elif action == "listimage":
        return list_image()
    return "upload"

@upload_blueprint.route("/title_pic", methods=["POST"])
def title_pic():
    res = {"state": "FAILURE", "url": "", "title": "", "original": ""}
    upfile = request.files.get("title_pic", None)

    # Respond with a string that is javascript code contained in html tags. This code will be executed by the
    # element that is defined in the `target` attribute of the html form, which is the <iframe> element
    # We want the <iframe> element to execute js code defined in set.js, which belongs to food/set.html, its parent.
    # The method .upload.error() is defined by us in set.js
    if upfile is None:
        return tag_js("window.parent.upload.error('上传失败')")

    upload_res = upload_by_file(upfile)
    if upload_res["code"] != 200:
        return tag_js("window.parent.upload.error('上传失败: %s')" % upload_res['msg'])

    return tag_js("window.parent.upload.success('%s')" % upload_res["data"]["file_key"])

def tag_js(script):
    return "<script type='text/javascript'>%s</script>" % script

def upload_image():
    """ Save image to server """
    # initialize json dict to return to ueditor
    res = {"state": "FAILURE", "url": "", "title": "", "original": ""}
    upfile = request.files.get("upfile", None)

    if upfile is None:
        return make_response(jsonify(res))

    upload_res = upload_by_file(upfile)
    if upload_res["code"] != 200:
        res["state"] = "FAILURE: " + upload_res["msg"]
        return make_response(jsonify(res))

    res["state"] = "SUCCESS"
    # the url field in res is important for front-end url editor to retrieve image from backend and show in editor
    res["url"] = build_image_url(upload_res["data"]["file_key"])

    return make_response(jsonify(res))

def list_image():
    """ List the url of all images that are uploaded """
    res = {"state": "FAILURE", "list": [], "start": 0, "total": 0}
    start = int(request.values.get("start", "0"))
    page_size = int(request.values.get("size", "20"))

    # managing offset for pagination effect in image list display
    query = Image.query
    if start > 0:
        query = query.filter(Image.id > start)

    # get list of images from database query
    img_info_list = query.order_by(Image.id.desc()).limit(page_size).all()
    if img_info_list:
        img_list = [{"url": build_image_url(img.file_key)} for img in img_info_list]
    else:
        return res

    res["start"] = img_info_list[-1].id
    res["state"] = "SUCCESS"
    res["list"] = img_list
    res["total"] = len(img_list)
    return make_response(jsonify(res))