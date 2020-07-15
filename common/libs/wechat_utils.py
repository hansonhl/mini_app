from application import app
import xml.etree.ElementTree as ET
import hashlib, requests, uuid, time

from common.libs.utils import json_response, json_error_response, get_current_time

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
        if prepay_id is None:
            return json_error_response("支付失败，请稍后再试（4）")
        prepay_data = {
            "appid": pay_data.get("appid"),
            "noncestr": pay_data.get("noncestr"),
            "package": "prepay_id=" + prepay_id,
            "sign_type": "MD5",
            "timestamp": str(int(time.time()))
        }
    return

def create_sign(pay_data):
    s = "&".join("%s=%s" % (k, v) for k, v in sorted(pay_data.items()))
    s = s + "&key=" + app.config["PAY_API_SECRET_KEY"]
    sign = hashlib.md5(s.encode("utf-8")).hexdigest()
    return sign.upper()

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