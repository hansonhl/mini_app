from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from common.libs.url_manager import build_url, build_static_url
import os

class Application(Flask):
    def __init__(self, import_name, template_folder="", static_folder=""):
        super(Application, self).__init__(import_name,
                                          template_folder=template_folder,
                                          static_folder=static_folder)
        self.config.from_pyfile("config/base_setting.py")


templates_dir = os.path.join(os.getcwd(), "web", "templates")
static_dir = os.path.join(os.getcwd(), "web", "static")
app = Application(__name__, templates_dir, static_dir)

# configuration settings
# export MINI_ENV=dev|demo|prod
# python3 main.py
if "MINI_ENV" in os.environ:
    app.config.from_pyfile("config/%s_setting.py" % (os.environ["MINI_ENV"]))

db = SQLAlchemy(app)

# register python function as part of html template rendering
app.add_template_global(build_url, "buildUrl")
app.add_template_global(build_static_url, "buildStaticUrl")