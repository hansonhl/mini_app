import random, string, hashlib, base64

from common.libs.utils import json_error_response
from common.models.user import User

def generate_salted_pwd(password, salt):
    m = hashlib.md5()
    s = "%s-%s" % (base64.encodebytes(password.encode("utf-8")), salt)
    m.update(s.encode("utf-8"))
    return m.hexdigest()

def generate_salt(length=16):
    keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
    return ("".join(keylist))

def generate_auth_code(user_info):
    m = hashlib.md5()
    str = "%s-%s-%s-%s-%s" % (user_info.uid, user_info.login_name, user_info.login_pwd,
                              user_info.login_salt, user_info.status)
    m.update(str.encode("utf-8"))
    return m.hexdigest()

def generate_cookie(user_info):
    return "%s#%s" % (generate_auth_code(user_info), user_info.uid)

def check_login(request):
    username = request.form["login_name"] if "login_name" in request.form else ""
    pwd = request.form["login_pwd"] if "login_pwd" in request.form else ""

    if username is None or len(username) < 1 or pwd is None or len(pwd) < 1:
        return json_error_response("您的用户名或者密码不能为空!"), None

    user_info = User.query.filter_by(login_name=username).first()

    if user_info is None:
        return json_error_response("您的用户名或者密码有误，请确认!"), None

    salted_pwd = generate_salted_pwd(pwd, user_info.login_salt)
    if salted_pwd != user_info.login_pwd:
        return json_error_response("您的用户名或者密码有误，请确认!"), None

    if user_info.status != 1:
        return json_error_response("您的账户已被注销或者禁用，请联系管理员。"), user_info

    return None, user_info