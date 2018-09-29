# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/9/4 17:19'


from flask import g, request, jsonify, current_app
from flask_restful import Resource, fields, marshal
from acs.utils.commons import login_required
from acs.models import CustomerService, AimiChatLogs
from acs.ext import redis_store
import hashlib, json
from acs.rongcloud import RongCloud
from acs.tasks import rong_send_message, service_change_state


class ChangeServiceState(Resource):
    @login_required
    def post(self):
        user_id = g.user_id
        state = request.form.get('state', None)
        if not state:
            result = { "status": "404","msg": "error","data": "参数不完整"}
            return result
        service = CustomerService.query.filter_by(id=user_id,is_delete=0).first()
        service.state = state
        service.save()
        result = {
            "status": "200",
            "msg": "客服状态修改",
            "data": "客服状态变更成功"
        }
        return result


class ServiceShutWeb(Resource):
    @login_required
    def post(self):
        user_id = g.user_id
        service = CustomerService.query.filter_by(id=user_id,is_delete=0).first()
        service.state = "不在线"
        service.save()
        redis_robot_service = 'service' + str(service.robot_user_id)
        redis_robot_line = 'line' + str(service.robot_user_id)
        # redis_store.hincrby(redis_robot_service, service_id, amount=1)
        redis_store.hset(redis_robot_service, service.service_id, 0)
        # 如果所有客服都不在线,清空列表和客服接待数量
        # #移除列表内没有在该索引之内的值r.ltrim("list_name",0,2)
        all_service = CustomerService.query.filter_by(robot_user_id=service.robot_user_id,state='在线',is_delete=0).all()
        if not all_service:
            all_service = CustomerService.query.filter_by(robot_user_id=service.robot_user_id,is_delete=0).all()
            for service in all_service:
                redis_store.hset(redis_robot_service, service.service_id, 0)
            redis_store.ltrim(redis_robot_line, 0, 0)
            redis_store.lrem(redis_robot_line, 0, redis_store.lindex(redis_robot_line, 0))
            pass
        result = {
            "status": "200",
            "msg": "客服退出",
            "data": "客服状态变更为不在线,客服接待人数清空"
        }
        return result


class MessageRoute(Resource):
    # 服务端实时消息路由,service_user_id也要存
    # 融云服务器向应用服务器推送数据（调用应用服务器接口）时会添加 3 个 GET 请求参数（在 URL 上添加的参数），具体如下
    def post(self):
        args_dict = request.args
        nonce = args_dict.get('nonce', None) # 随机数,无长度限制
        timestamp = args_dict.get('signTimestamp') # 时间戳
        # Signature(数据签名)计算方法：将系统分配的AppSecret、Nonce(随机数)、Timestamp(时间戳)三个字符串按先后顺序拼接成一个字符串并进行SHA1哈希计算
        app_secret = 'QASsvdjF7j'
        signature = args_dict.get('signature', None)
        if not all([nonce, timestamp, signature]):
            result = {"status": "404","msg": "参数不完整"}
            return jsonify(result)
        hash_sha1 = hashlib.sha1((app_secret + nonce + timestamp).encode('utf-8')).hexdigest()
        if hash_sha1 != signature:
            result = {"status": "404", "msg": "传输数据非法!", "data": "请输入有效参数,及正确的签名代码."}
            return jsonify(result)
        message = request.form
        fromUserId = message.get('fromUserId', None) # dialocg_id
        toUserId = message.get('toUserId', None)
        objectName = message.get('objectName', None)
        content = eval(message.get('content', None))
        msgTimestamp = message.get('msgTimestamp', None)
        msgUID = message.get('msgUID', None)
        chat_content = content['content']
        if chat_content == '关闭客户会话,RongIMClient.getInstance().logout()':
            return 'success'
        try:
            customer_name= content['extra'][3]
            product_id = content['extra'][4]
            robot_code = content['extra'][0][:-3]
            from_id = CustomerService.query.filter_by(service_id=fromUserId,is_delete=0).first()
            if from_id:
                chat_log = AimiChatLogs(name=from_id.s_name, role='service', dialog_id=toUserId, user_id=from_id.robot_user_id,product_id=product_id,content=chat_content,robot_code=robot_code,service_user_id=from_id.id)
            else:
                from_id = CustomerService.query.filter_by(service_id=toUserId,is_delete=0).first()
                chat_log= AimiChatLogs(name=customer_name, role='customer', dialog_id=fromUserId, user_id=from_id.robot_user_id,product_id=product_id,content=chat_content,robot_code=robot_code,service_user_id=from_id.id)
            chat_log.save()
        except Exception as e:
            current_app.logger.error(e)
            result = {
                "status": "404",
                "msg": "extra携带信息错误,数据库操作异常!",
            }
            return result
        return 'success'




class ServiceOnlineStatus(Resource):
    # 客服状态在线订阅
    # 实时消息路由和在线状态订阅不同:时间戳:timestamp,signTimestamp
    # request.form request.get_json()
    def post(self):
        args_dict = request.args
        nonce = args_dict.get('nonce', None)
        timestamp = args_dict.get('timestamp')
        app_secret = 'QASsvdjF7j'
        signature = args_dict.get('signature', None)
        if not all([nonce, timestamp, signature]):
            result = {"status": "404", "msg": "参数不完整"}
            return jsonify(result)
        hash_sha1 = hashlib.sha1((app_secret + nonce + timestamp).encode('utf-8')).hexdigest()
        if hash_sha1 != signature:
            result = {"status": "404", "msg": "传输数据非法!", "data": "请输入有效参数,及正确的签名代码."}
            return jsonify(result)
        all_message = request.get_json()  # 获取json数据
        # all_user = [mes.get('userid') for mes in all_message]
        # for service in all_user:
        last_message = all_message[-1]
        from_id = CustomerService.query.filter_by(service_id=last_message.get('userid'), is_delete=0).first()
        try:
            if from_id:
                # id1 = [i for i, x in enumerate(all_user) if x == service]
                state = last_message.get('status')
                time = last_message.get('time')
                if state == '1' or state == '2':
                    redis_store.set(from_id.service_id + '1' + 'service', time)
                    service_change_state.delay(from_id.service_id)

                    '''
                    from_id.state = '不在线'
                    from_id.save()
                    redis_robot_service = 'service' + str(from_id.robot_user_id)
                    redis_robot_line = 'line' + str(from_id.robot_user_id)
                    # redis_store.hincrby(redis_robot_service, service_id, amount=1)
                    redis_store.hset(redis_robot_service, from_id.service_id, 0)
                    # 如果所有客服都不在线,清空列表和客服接待数量
                    # #移除列表内没有在该索引之内的值r.ltrim("list_name",0,2)
                    all_service = CustomerService.query.filter_by(robot_user_id=from_id.robot_user_id, state='在线',is_delete=0).all()
                    if not all_service:
                        all_service = CustomerService.query.filter_by(robot_user_id=from_id.robot_user_id,is_delete=0).all()
                        for service in all_service:
                            redis_store.hset(redis_robot_service, service.service_id, 0)
                        redis_store.ltrim(redis_robot_line, 0, 0)
                        redis_store.lrem(redis_robot_line, 0, redis_store.lindex(redis_robot_line, 0))
                    pass
                    '''
                elif state == '0':
                    redis_store.set(from_id.service_id+ '0' + 'service', time)
            else:
                state = last_message.get('status')
                userid = last_message.get('userid')
                redis_status = 'status' + last_message.get('userid')
                time = last_message.get('time')
                service_id = redis_store.get(redis_status).decode()
                from_id = CustomerService.query.filter_by(service_id=service_id, is_delete=0).first()
                redis_robot_service = 'service' + str(from_id.robot_user_id)
                if (len(all_message) == 1) and (state == '1' or state == '2'):
                    redis_store.hincrby(redis_robot_service, service_id, amount=-1)
                    redis_store.set(userid + '1' + 'customer', time)
                    # app_key = 'z3v5yqkbz1h60'
                    # app_secret = 'QASsvdjF7j'
                    # rcloud = RongCloud(app_key, app_secret)
                    # r = rcloud.Message.publishPrivate(
                    #     fromUserId=last_message.get('userid'),
                    #     toUserId=service_id,
                    #     objectName='RC:TxtMsg',
                    #     content=json.dumps({"content": "关闭客户会话,RongIMClient.getInstance().logout()", "extra": "helloExtra"}),
                    #     isPersisted='1',
                    #     isCounted='1', )
                    rong_send_message.delay(userid, service_id)
                    redis_store.delete(redis_status)
                elif (len(all_message) > 1) and (state == '1' or state == '2'):
                    redis_store.hincrby(redis_robot_service, service_id, amount=-1)
                elif state == '0':
                    redis_store.set(userid+state + 'customer', time)
                if int(redis_store.hget(redis_robot_service, service_id).decode()) < 0:
                    redis_store.hset(redis_robot_service, service_id, 0)
            return 'success'
        except:
            return 'fail'

    def get(self):
        service_id = 'c81e728d9d4c2f636f067f89cc14862c'
        service_change_state.delay(service_id)
        print('hello')
        return 'success'










