DEBUG = False
SERVER_PORT = 5000

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf8mb4"
SQLALCHEMY_DATABASE_URI = "mysql://root:Sena_Kwenda_luga10@127.0.0.1/food_db"

SECRET_KEY = "my_mini_web_app"
DEBUG_TB_INTERCEPT_REDIRECTS = False
AUTH_COOKIE_NAME = "mina_admin"

IGNORE_COOKIE_AUTH_URLS = [
    "^/user/login",
    "^/static",
    "^/favicon.ico"
] # use regexp

ACCOUNT_INDEX_USERS_PER_PAGE = 30