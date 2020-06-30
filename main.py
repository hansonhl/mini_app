from application import app
from routing import *

from flask_script import Manager, Server
import sys, traceback

manager = Manager(app)
manager.add_command("runserver", Server(host="0.0.0.0", port=app.config["SERVER_PORT"], use_debugger=True))

def main():
    manager.run()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        traceback.print_exc()