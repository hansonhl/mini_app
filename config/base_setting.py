import json

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

IGNORE_API_AUTH_URLS = [
    "^/api/member/login",
    "^/api/member/check-reg",
    "^/api/food/index"
]

ACCOUNT_INDEX_ITEMS_PER_PAGE = 30
MEMBER_INDEX_ITEMS_PER_PAGE = 30
FOOD_CAT_ITEMS_PER_PAGE = 30
FOOD_INDEX_ITEMS_PER_PAGE = 30
APP_FOOD_INDEX_ITEMS_PER_PAGE = 4

PAY_WAIT_TIME = 30 # (minutes) allowed time duration between user creates order and pays for it

ACCOUNT_STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
}

IMG_UPLOAD_CONFIGS = {
    "allowed_extensions": {"jpg", "gif", "tmp", "jpeg", "png"},
    "prefix_path": "/web/static/upload/",
    "prefix_url": "/static/upload/"
}

DOMAIN = "http://192.168.1.171:5000"

PAY_STATUS_MAPPING = {
    "0": "订单已关闭",
    "1": "支付成功",
    "-8": "待支付",
    "-7": "待发货",
    "-6": "待确认",
    "-5": "待评价"
}

with open("city_info.json", "r") as f:
    addr_info = json.load(f)

PROV_ID_TO_IDX_MAP = {province["id"]: i for i, province in enumerate(addr_info)}
CITY_ID_TO_IDX_MAPS = [{city["id"]: i for i, city in enumerate(province["cityList"])}
                       for province in addr_info]
DISTR_ID_TO_IDX_MAPS = [[{district["id"]: i for i, district in enumerate(city["districtList"])}
                        for city in province["cityList"]]
                       for province in addr_info]