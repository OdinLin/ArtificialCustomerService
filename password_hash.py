# -*- coding:utf-8 -*-

from werkzeug import security


def password(origin_password):
    """
    对应额外添加的属性password的设置行为
    : params origin_password: 在进行属性设置的时候，要设置的值  # user.password = origin_password
    :return:
    """
    # 密码加密
    password_hash = security.generate_password_hash(origin_password)
    # 密码解密 check_password_hash(hash,password)
    return password_hash


print(password('12345678'))

import hashlib

print(hashlib.md5('4'.encode('utf-8')).hexdigest())

# print(type({'hello':'world'}))
# if isinstance({'hello':'world'}, dict):
#     print(True)



app_secret = 'QASsvdjF7j'
nonce = '1234'
# timestamp = '1234567890'

# hash_sha1 = hashlib.sha1((app_secret + nonce + timestamp).encode('utf-8')).hexdigest()
# print(hash_sha1)

import time

# 输入毫秒级的时间，转出正常格式的时间
def timeStamp(timeNum):
    timeStamp = float(timeNum/1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(otherStyleTime)
    return otherStyleTime
dt1 = timeStamp(1538126919059)
dt2 = timeStamp(1538127228398)

dt3 = timeStamp(1538126808478)
dt4 = timeStamp(1538126808182)



# 1538126919059  1538127228398

# 1538126808478  1538126808182