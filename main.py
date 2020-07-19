from application import app, manager
from routing import *

from flask_script import Server
import sys, traceback
from jobs.launcher import Job


manager.add_command("runserver", Server(host="0.0.0.0", port=app.config["SERVER_PORT"], use_debugger=True))

# job entrance
manager.add_command("run", Job())


def main():
    manager.run()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        traceback.print_exc()