import json
from common.models.app_access_log import AppAccessLog
from common.libs.utils import get_current_time

from application import app, db

def add_access_log(request, g):
    entry = AppAccessLog()
    entry.target_url = request.url
    entry.referer_url = request.referrer
    entry.ip = request.remote_addr
    entry.query_params = json.dumps(request.values.to_dict())

    if "current_user" in g and g.current_user is not None:
        entry.uid = g.current_user.uid

    entry.ua = request.headers.get("User-Agent")
    entry.created_time = get_current_time()

    db.session.add(entry)
    db.session.commit()
    return True


def add_error_log():
    pass