DEBUG = False
SERVER_PORT = 5000

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf8mb4"

SECRET_FILE = "secret.py"


DEBUG_TB_INTERCEPT_REDIRECTS = False
AUTH_COOKIE_NAME = "mina_admin"

IGNORE_COOKIE_AUTH_URLS = [
    "^/user/login",
    "^/static",
    "^/favicon.ico",
    "^/api"
] # use regexp

ACCOUNT_INDEX_ITEMS_PER_PAGE = 30
MEMBER_INDEX_ITEMS_PER_PAGE = 30
FOOD_CAT_ITEMS_PER_PAGE = 30

ACCOUNT_STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
}

IMG_UPLOAD_CONFIGS = {
    "allowed_extensions": {"jpg", "gif", "tmp", "jpeg", "png"},
    "prefix_path": "/web/static/upload/",
    "prefix_url": "/static/upload/"
}

APP_CONFIGS = {
    "domain": "http://192.168.1.171:5000"
}