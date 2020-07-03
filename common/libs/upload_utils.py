import os, stat, uuid

from common.libs.utils import get_current_time
from common.models.images import Image

from werkzeug.utils import secure_filename
from application import app, db

def upload_by_file(f):
    res = {"code": -1, "msg": "", "data": {}}
    filename = secure_filename(f.filename)
    extension = filename.rsplit(".", maxsplit=1)[1]

    # check if ext is in our predefined list of extensions
    img_upload_configs = app.config["IMG_UPLOAD_CONFIGS"]
    if extension not in img_upload_configs["allowed_extensions"]:
        res["msg"] = "不允许的扩展类型文件"
        return res

    # save uploaded file locally, check and create directory for files uploaded each day
    file_dir = get_current_time("%Y%m%d")
    save_dir = os.path.join(app.root_path, img_upload_configs["prefix_path"].strip("/"), file_dir)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO) # 747

    # generate unique identifier and save file to server
    file_name = str(uuid.uuid4()).replace("-", "") + "." + extension
    file_key = os.path.join(file_dir, file_name)
    file_path = os.path.join(save_dir, file_name)
    f.save(file_path)
    app.logger.info("Saved uploaded image at %s" % file_path)

    image_info = Image()
    image_info.file_key = file_key
    image_info.created_time = get_current_time()
    db.session.add(image_info)
    db.session.commit()

    res["code"] = 200
    res["msg"] = "上传文件成功"
    res["data"] = {"file_key": file_key}
    return res

