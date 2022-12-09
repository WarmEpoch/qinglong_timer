import requests
import re
import json
import base64
import threading
import time
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


class Env:
    # iPhone 13 Pro
    UserAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                'Mobile/15E148 yiban_iOS/5.0.8 '
    # Chrome浏览器
    UserAgent2 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/96.0.4664.110 Safari/537.36 '

    # 微信浏览器
    UserAgent3 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 ' \
                 'Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6305002e) '
                 
env = Env()


public_key = '''-----BEGIN PUBLIC KEY-----
    MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA6aTDM8BhCS8O0wlx2KzA
    Ajffez4G4A/QSnn1ZDuvLRbKBHm0vVBtBhD03QUnnHXvqigsOOwr4onUeNljegIC
    XC9h5exLFidQVB58MBjItMA81YVlZKBY9zth1neHeRTWlFTCx+WasvbS0HuYpF8+
    KPl7LJPjtI4XAAOLBntQGnPwCX2Ff/LgwqkZbOrHHkN444iLmViCXxNUDUMUR9bP
    A9/I5kwfyZ/mM5m8+IPhSXZ0f2uw1WLov1P4aeKkaaKCf5eL3n7/2vgq7kw2qSmR
    AGBZzW45PsjOEvygXFOy2n7AXL9nHogDiMdbe4aY2VT70sl0ccc4uvVOvVBMinOp
    d2rEpX0/8YE0dRXxukrM7i+r6lWy1lSKbP+0tQxQHNa/Cjg5W3uU+W9YmNUFc1w/
    7QT4SZrnRBEo++Xf9D3YNaOCFZXhy63IpY4eTQCJFQcXdnRbTXEdC3CtWNd7SV/h
    mfJYekb3GEV+10xLOvpe/+tCTeCDpFDJP6UuzLXBBADL2oV3D56hYlOlscjBokNU
    AYYlWgfwA91NjDsWW9mwapm/eLs4FNyH0JcMFTWH9dnl8B7PCUra/Lg/IVv6HkFE
    uCL7hVXGMbw2BZuCIC2VG1ZQ6QD64X8g5zL+HDsusQDbEJV2ZtojalTIjpxMksbR
    ZRsH+P3+NNOZOEwUdjJUAx8CAwEAAQ==
    -----END PUBLIC KEY-----'''

def encrypt_password(password, public_key):
    cipher = PKCS1_v1_5.new(RSA.importKey(public_key))
    cipher_text = base64.b64encode(cipher.encrypt(bytes(password, encoding="utf8")))
    return cipher_text.decode("utf-8")

def chrome_login(account, password):
        session = requests.session()
        headers = {
            'User-Agent': env.UserAgent2,
        }
        html = session.get("https://www.yiban.cn/login", headers=headers).text
        keysTime = re.findall(r"data-keys-time='(.*?)'", html)[0]
        keys = re.findall(r"data-keys='(.*?[^%&',;=?$\x22]+)'", html)[0]
        data = {
            'account': account,  # 填写账号
            'password': encrypt_password(password, keys),  # 密码Rsa加密
            'captcha': '',
            'keysTime': keysTime,
        }
        url = "https://www.yiban.cn/login/doLoginAjax"
        resp = session.post(url, data=data)
        response = resp.json()
        response['yiban_user_token'] = resp.cookies.get('yiban_user_token')
        return response

def GetPostList():
    url = 'https://s.yiban.cn/api/forum/getListByBoard?offset=0&count=30&boardId=0p0Iaz1ymYMradR&orgId=2004312'
    res = requests.get(url).json()
    return res['data']['list']

def UpThumb(list,token,userId):
    for n in list:
        url = "https://s.yiban.cn/api/post/thumb"
        params = {
            'action': 'up',
            'postId': n['id'],
            'userId': userId
        }
        headers = {
            'User-Agent': env.UserAgent2,
            'Cookie': 'yiban_user_token=' + token
        }
        res = requests.post(url, data=json.dumps(params, indent=2), headers=headers).json()
        print({'id': userId, 'data': res, 'time': time.time()})
        time.sleep(4)

def GetUser(token):
    url = 'https://s.yiban.cn/api/my/getInfo'
    headers = {
        'User-Agent': env.UserAgent2,
        'Cookie': 'yiban_user_token=' + token
    }
    res = requests.get(url, headers=headers).json()
    return res

if __name__ == '__main__':
    loginList = [
        {'login': '15019744482','pwd': '10086hst'},
        {'login': '18023744377','pwd': 'A2901377401'},
        {'login': '16620192839','pwd': 'Chen2003'}
    ]
    for i in loginList:
        token = chrome_login(i['login'],i['pwd'])['yiban_user_token']
        userId = GetUser(token)['data']['userId']
        postList = GetPostList()
        thumb = threading.Thread(target=UpThumb, args=(postList, token , userId))
        thumb.start()
