from flask import Blueprint

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/")
def index():
    return "mini api v1.0"

from web.controllers.api.member import *
from web.controllers.api.food import *
# allows code in api modules to be imported when simply importing web.controllers.api in other modules
# this line must be after the definition of api_blueprint, because other api modules depend on it