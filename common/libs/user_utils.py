import random, string, hashlib, base64

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