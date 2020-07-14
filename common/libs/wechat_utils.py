from application import app
import xml.etree.ElementTree as ET
import hashlib
import requests

def get_pay_info(pay_data=None):
    """获取支付信息"""
    sign = create_sign(pay_data)
    pay_data["sign"] = sign
    xml_data = dict_to_xml(pay_data)
    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    return


def create_sign(pay_data):
    s = "&".join("%s=%s" % (k, v) for k, v in sorted(pay_data.items()))
    s = s + "&key=" + app.config["PAY_API_SECRET_KEY"]
    sign = hashlib.md5(s.encode("utf-8")).hexdigest()
    return sign.upper()

def dict_to_xml(d):
    xml = ["<xml>"] + ["<{0}>{1}</{0}>".format(k, v) for k, v in d.items()] + ["</xml>"]
    return "".join(xml)

def xml_to_dict(xml):
    res = {}
    root = ET.fromstring(xml)
    for child in root:
        res[child.tag] = child.text
    return res