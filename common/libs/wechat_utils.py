from application import app, db
import xml.etree.ElementTree as ET
import hashlib, requests, uuid, time, datetime, json

from common.libs.utils import  get_current_time
from common.models.oauth_access_token import OauthAccessToken

def get_pay_info(pay_data=None):
    """ Goal: obtain `prepay_id` from WeChat official api.
    Packages up data in xml format, and processes response from WeChat """
    sign = create_sign(pay_data)
    pay_data["sign"] = sign
    xml_data = dict_to_xml(pay_data)
    headers = {
        "Content-Type": "application/xml"
    }
    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    r = requests.post(url=url, data=xml_data.encode("utf-8"), headers=headers)
    r.encoding = "utf-8"

    app.logger.debug("Request sent:\n%s" % r.text)
    if r.status_code == 200:
        prepay_id = xml_to_dict(r.text).get("prepay_id", None)

        if prepay_id is None and not app.config["DEV_MODE"]:
            return None

        if app.config["DEV_MODE"] and prepay_id is None:
            prepay_id = pay_data["out_trade_no"]

        prepay_data = {
            "appId": pay_data.get("appid"),
            "nonceStr": pay_data.get("nonce_str"),
            "package": "prepay_id=" + prepay_id,
            "signType": "MD5",
            "timeStamp": str(int(time.time())),
        }
        prepay_sign = create_sign(prepay_data)
        prepay_data.pop("appId")
        prepay_data["paySign"] = prepay_sign
        prepay_data["prepay_id"] = prepay_id

        return prepay_data
    else:
        return None

def create_sign(pay_data):
    s = "&".join("%s=%s" % (k, pay_data[k]) for k in sorted(pay_data))
    s = s + "&key=" + app.config["PAY_API_SECRET_KEY"]
    sign = hashlib.md5(s.encode("utf-8")).hexdigest().upper()
    return sign

def dict_to_xml(d):
    xml = ["<xml>"] + ["<{0}>{1}</{0}>".format(k, v) for k, v in d.items()] + \
          ["</xml>"]
    return "".join(xml)

def xml_to_dict(xml):
    res = {}
    root = ET.fromstring(xml)
    for child in root:
        res[child.tag] = child.text
    return res

def get_nonce_str():
    """ Basically get a random string """
    return str(uuid.uuid4()).replace("-", "")

def get_access_token():
    token_info = OauthAccessToken.query.filter(OauthAccessToken.expired_time > get_current_time()).first()
    if token_info:
        return token_info.access_token

    appid = app.config["MINA_APP_ID"]
    appsecret = app.config["MINA_APP_SECRET"]
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" \
        % (appid, appsecret)

    r = requests.get(url=url)

    if r.status_code != 200 or not r.text:
        app.logger.error("获取access_token失败！")
        return None

    data = json.loads(r.text)
    now = datetime.datetime.now()
    expired_date = now + datetime.timedelta(seconds=data["expires_in"])
    token_info = OauthAccessToken()
    token_info.access_token = data["access_token"]
    token_info.expired_time = expired_date.strftime("%Y-%m-%d %H:%M:%S")
    token_info.created_time = now.strftime("%Y-%m-%d %H:%M:%S")

    db.session.add(token_info)
    db.session.commit()

    return data