# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/10/9 11:57'

# coding:utf-8
from acs.rongcloud import RongCloud
from acs.ext import redis_store
from celery import Celery
import time, json



broker_url = "redis://127.0.0.1:6379/10"

result_backend = "redis://127.0.0.1:6379/10"




# 创建celery应用对象
celery_app = Celery("tasks", broker=broker_url)


@celery_app.task
def rong_send_message(userid, service_id):
    time.sleep(5)
    start_time = redis_store.get(userid + '0' + 'customer')
    end_time = redis_store.get(userid + '1' + 'customer')
    if not all([start_time, end_time]):
        return 'not send'
    if start_time > end_time:
        return 'refresh not send'
    app_key = 'z3v5yqkbz1h60'
    app_secret = 'QASsvdjF7j'
    rcloud = RongCloud(app_key, app_secret)
    r = rcloud.Message.publishPrivate(
        fromUserId=userid,
        toUserId=service_id,
        objectName='RC:TxtMsg',
        content=json.dumps({"content": "592b71f0-b3f8-4f64-bd45-40b35c0191af", "extra": "helloExtra"}),
        isPersisted='1',
        isCounted='1', )
    redis_store.delete(userid + '0' + 'customer')
    redis_store.delete(userid + '1' + 'customer')
    return 'send_success'



@celery_app.task
def service_change_state(service_id):
    time.sleep(5)
    start_time = redis_store.get(service_id + '0' + 'service')
    end_time = redis_store.get(service_id + '1' + 'service')
    if not all([start_time, end_time]):
        return 'not send'
    if start_time > end_time:
        return 'refresh not send'
    try:
        import pymysql
        connection = pymysql.connect(host='127.0.0.1', user='root', password="qbzz@2018",
                                     database='cms', port=3306, db='python', charset='utf8')
        with connection.cursor() as cursor:
            sql = 'select robot_user_id, service_id from customer_service where service_id = "%s" and is_delete=0' % (
                service_id)
            cursor.execute(sql)
            results = cursor.fetchone()
            robot_user_id = results[0]
            cursor.execute('update customer_service set state = "%s" where service_id = "%s"' % ('不在线',service_id))
            redis_robot_service = 'service' + str(robot_user_id)
            # redis_store.hincrby(redis_robot_service, service_id, amount=1)
            redis_store.hset(redis_robot_service, service_id, 0)
            redis_store.delete(service_id + '0' + 'service')
            redis_store.delete(service_id + '1' + 'service')
            connection.commit()
    except:
        pass
    return 'send_success'




def test():
    service_id = 'c81e728d9d4c2f636f067f89cc14862c'
    service_change_state.delay(service_id)
    print('hello')

# celery -A acs.tasks worker --loglevel=info -P eventlet

# celery -A acs.tasks.celery_app worker --loglevel=info    选择这个!
# celery -A acs --app=acs.tasks:celery_app worker --loglevel=info

if __name__ == '__main__':
    test()





