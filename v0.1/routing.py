from web.controllers.index import index_blueprint
from web.controllers.imooc import route_imooc
from web.controllers.user.user import user_blueprint
from web.controllers.account.account import account_bluprint
from web.controllers.member.member import member_blueprint
from web.controllers.food.food import food_blueprint
from web.controllers.finance.finance import finance_blueprint
from web.controllers.stat.stat import stat_blueprint

from web.interceptors.errorhandlers import *

app.register_blueprint(index_blueprint, url_prefix="/")
app.register_blueprint(route_imooc, url_prefix="/imooc")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(account_bluprint, url_prefix="/account")
app.register_blueprint(member_blueprint, url_prefix="/member")
app.register_blueprint(food_blueprint, url_prefix="/food")
app.register_blueprint(finance_blueprint, url_prefix="/finance")
app.register_blueprint(stat_blueprint, url_prefix="/stat")