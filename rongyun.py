# -*- coding:utf-8 -*-
__author__ = 'zhangzhibo'
__date__ = '2018/8/21 14:56'
from acs.rongcloud import RongCloud


app_key = 'z3v5yqkbz1h60'
app_secret = 'QASsvdjF7j'
rcloud = RongCloud(app_key, app_secret)
s = rcloud.User.checkOnline(userId='userid3')
# 在线状态，1为在线，0为不在线。
# print(s.result['status'])


app_key = '82hegw5u8ytdx'
app_secret = 'Zmc9oahKBk9oQY'
rcloud = RongCloud(app_key, app_secret)
r = rcloud.User.getToken(userId='c81e728d9d4c2f636f067f89cc14862cqbkj', name='Harry', portraitUri='')
print(r.result['token'])


# userid1:SWPgbuJCfwrx2/xHmNz6FFfbRjwhmykJ5L0M1IUIFLvHW44JBDS2g67wPwAW+7Is/HzdC4xCbhveV8UwmFF5/g==
# userid2: Eq7rUIjpD/rx2/xHmNz6FFfbRjwhmykJ5L0M1IUIFLvHW44JBDS2gzQ7fPYzNzSs/HzdC4xCbhufiVov5eSczA==




#############################################################
import requests, random, time, hashlib

def sendToIM(url, data):
    a = random.randint(0,9)
    b = random.randint(0,9)
    c = random.randint(0,9)
    d = random.randint(0,9)
    str_random = str(a) + str(b) + str(c) + str(d)
    str_time = str(int(time.time()))
    app_secret = 'QASsvdjF7j'
    signature = hashlib.sha1((app_secret + str_random + str_time).encode('utf-8')).hexdigest()
    headers = {'App-Key': 'z3v5yqkbz1h60',
               'Nonce': str_random,
               'Timestamp':str_time,
               'Signature': signature,
               "Content-Type":"application/x-www-form-urlencoded;charset=utf-8"}

    data = data
    url = url
    a = requests.post(url,headers=headers, data=data)
    return a.json()

if __name__ == '__main__':
    a = sendToIM('http://api.cn.ronghub.com/user/getToken.json', {'userId':'c81e728d9d4c2f636f067f89cc14862c','name':'小不点'})
    #print(a['token'])


    # RoBW0UiEH9D6ptJTiZ2odVRNJCcB1D9904%2F%2BRbBj12WQOoeQDu%2FbuTzLZXP2Tp%2BcZEUuGMXLXJ%2FCmo8b21xX4jAw4o7vMcrKGXhhy2pY%2FL0vOHTVpZB5fI0icdrrrkI1
    # RoBW0UiEH9D6ptJTiZ2odVRNJCcB1D9904/+RbBj12WQOoeQDu/buTzLZXP2Tp+cZEUuGMXLXJ/Cmo8b21xX4jAw4o7vMcrKGXhhy2pY/L0vOHTVpZB5fI0icdrrrkI1

