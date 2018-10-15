# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/9/5 16:25'
from acs.ext import redis_store

redis_test = redis_store
# 机器人编号-->客服编号-->客户数量
redis_test.hset("service1","c81e728d9d4c2f636f067f89cc14862c",20)
# redis_test.hset("robot_002","c4ca4238a0b923820dcc509a6f75849b",2)

# print(str(redis_test.hget("robot_001","c4ca4238a0b923820dcc509a6f"),encoding='utf-8'))
print(redis_test.hgetall("robot_001"))

# print(r.hmget("hash1", "k1", "k2")) # 多个取hash的key对应的值


# print(redis_test.hlen("robot_001")) # 键值对个数
# print(redis_test.hkeys("robot_001")[0].decode())  # 所有键
# print(redis_test.hvals("robot_001")) # 所有值


# print(redis_store.hincrby("demo","a",amount=5))   # 自增自减
# print(redis_store.hmget("demo", "a"))
# print(type(redis_test.hget("robot_001","c4ca4238a0b923820dcc509a6f").decode()))
# redis_test.hset("demo", "b", 0)
 # 排队 机器人-->list[]


# 排队 用户id --> 客服 此客服刚好有时间

# print(redis_test.hget("demo","c").decode())
# redis_store.setex('1111111111111', 60, 5000)
a = redis_store.set('1111111111111', 0, None)


r = redis_store
# 删除, 增加(重复问题), 取出所有值
# r.rpush("list2", 44, 55, 66, 1, 2, 3)    # 在列表的右边，依次添加44,55,66
# print(r.llen("list2"))  # 列表长
s = r.lrange("list2", 0, -1)
# print(s)


s = r.ltrim("list2",0,0)
qwe = r.lrem('list2', 0, r.lindex("list2",0))

# print(qwe)
s = r.lrange("list2", 0, -1)
# print(s)



# if bytes('44',encoding='utf-8') in s:
#     print(s.index(bytes('66',encoding='utf-8')))
# str='zifuchuang'
# a = b'zifuchuang'
# b = bytes('zifuchuang',encoding='utf-8')
# c = ('zifuchuang').encode('utf-8')


# print(r.lrem("list2", 0, 66))
# 删除r.lrem(name, value, num)  lpop(name) lindex(name, index)根据索引获取值
# print(r.lindex('list2', 0))

# a = ['001机器人', '平安一年期综合意外险', ['理赔后资料能否取回?', '对于需要取回的资料,等等等']]
# print(a[0][:-3])
# a = redis_store.lpop('line1')
print(redis_store.lrange("line1",0,-1))



li = [{'status': '1', 'time': 1536996351755, 'os': 'Websocket', 'userid': 'userid5'}, {'status': '0', 'time': 1536996352471, 'os': 'Websocket', 'userid': 'userid5'}]
all_user = [mes.get('userid') for mes in li]

X = [1, 2, 3, 4, 2]
id1 = [i for i,x in enumerate(X) if x==2]
# print(id1[-1])
print(id1)




# redis_store.setex('hhhhhhh', 60, 5000)

print(redis_store.get('hhhhhhh'))

# redis_store.set('hhhhhhh', 0)
# print(redis_store.get('hhhhhhh').decode())
redis_store.delete('hhhhhhh')
if not redis_store.get('hhhhhhh'):
    print('无')


# r.rpush("sssssssssssssss", 44, 55, 66, 1, 2, 3)
# qq = redis_store.setex('hello,world', 60, redis_store.lpop("sssssssssssssss"))
# print(qq)


redis_store.setex('12345', 60 * 2, 1)

refresh_flag = redis_store.get('12345').decode()
print(refresh_flag)
if refresh_flag == '1':
    print(refresh_flag)



