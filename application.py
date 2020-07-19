from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_script import Manager
import os, json

class Application(Flask):
    def __init__(self, import_name, template_folder="", static_folder=""):
        super(Application, self).__init__(import_name,
                                          template_folder=template_folder,
                                          static_folder=static_folder)
        self.config.from_pyfile("config/base_setting.py")

        # configuration settings
        # export MINI_ENV=dev|demo|prod
        # python3 main.py
        self.environ = "dev"
        if "MINI_ENV" in os.environ:
            if os.environ["MINI_ENV"] in ["dev", "demo", "prod"]:
                self.environ = os.environ["MINI_ENV"]
            else:
                self.logger.error("The environment specified is invalid! Using dev by default. Must be one of: dev | demo | prod")

        self.config.from_pyfile("config/%s_setting.py" % self.environ)

        # load secret keys
        self.config.from_pyfile(self.config["SECRET_FILE"])




templates_dir = os.path.join(os.getcwd(), "web", "templates")
static_dir = os.path.join(os.getcwd(), "web", "static")

app = Application(__name__, templates_dir, static_dir)

db = SQLAlchemy(app)

manager = Manager(app)