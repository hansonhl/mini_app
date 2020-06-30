import os
from application import app
from common.libs.utils import get_current_time


def build_url(path):
    if "DOMAIN" in app.config:
        path = app.config["DOMAIN"]['www'] + path
    return path

def build_static_url(path):
    path = "/static" + path + "?ver=" + get_release_version()
    return build_url(path)

def get_release_version():
    ver = get_current_time("%Y%m%d%H%M%S")
    # release_path = app.config.get('RELEASE_PATH')
    # if release_path and os.path.exists(release_path):
    #     with open(release_path, 'r') as f:
    #         ver = f.readline()
    return app.config.get("RELEASE_VERSION", ver)