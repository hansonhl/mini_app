from application import app
from flask import request
from common.libs.utils import render_template_with_global_vars
from common.libs.log_service import add_error_log

@app.errorhandler(404)
def error_404(e):
    app.logger.error(e)
    ctx = {"status": 404, "msg": "很抱歉，您访问的页面不存在"}
    add_error_log(str(e), request)
    return render_template_with_global_vars("error/error.html", context=ctx)