from web.controllers.index import index_blueprint
from web.controllers.imooc import route_imooc
from web.controllers.user.user import user_blueprint
from web.controllers.account.account import account_bluprint

from web.interceptors.errorhandlers import *

app.register_blueprint(index_blueprint, url_prefix="/")
app.register_blueprint(route_imooc, url_prefix="/imooc")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(account_bluprint, url_prefix="/account")