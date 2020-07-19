from application import app, db
from common.models.queue_list import QueueList
from common.libs.utils import get_current_time

import json


def push(queue_name, data=None):
    new_queue_info = QueueList()
    new_queue_info.queue_name = queue_name
    if data:
        new_queue_info.data = json.dumps(data)
    new_queue_info.created_time = new_queue_info.updated_time = get_current_time()

    db.session.add(new_queue_info)
    db.session.commit()
