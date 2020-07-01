import random, string, requests, json, hashlib
from application import app

def generate_salt(length=16):
    keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
    return ("".join(keylist))

def generate_auth_code(member_info):
    m = hashlib.md5()
    str = "%s-%s-%s" % (member_info.id, member_info.salt, member_info.status)
    m.update(str.encode("utf-8"))
    return m.hexdigest()


def get_wechat_openid(login_code):
    url = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code" \
          % (app.config["MINA_APP_ID"], app.config["MINA_APP_SECRET"], login_code)
    res = json.loads(requests.get(url).text)
    res = res["openid"] if "openid" in res else None
    return res

def generate_token(member_info):
    return "%s#%s" % (generate_auth_code(member_info), member_info.id)