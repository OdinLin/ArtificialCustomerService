# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/9/4 17:18'


from flask import g, request, current_app, jsonify
from flask_restful import Resource, fields, marshal
from acs.rongcloud import RongCloud
from acs.models import CustomerService, AimiChatLogs, Product, RobotSettings
from acs.ext import redis_store
import time




class CustomerLogin(Resource):
    def post(self):
        '''客户点击人工客服登录'''
        usermessage = request.form
        uuid = usermessage.get('uuid', None)
        customer_name = usermessage.get('name', None)
        product_id = usermessage.get('product_id', None)
        robot_user_id = usermessage.get('robot_user_id', None)
        redis_robot_service = 'service' + str(robot_user_id)
        redis_robot_line = 'line' + str(robot_user_id)
        # 校验参数
        if not all([uuid, product_id, robot_user_id, customer_name]):
            result = { "status": "404","msg": "error","data": "参数不完整"}
            return result

        # 判断是否能接入客户 客服状态('在线,不在线')---机器人对应客服  客服接待数量
        service = CustomerService.query.filter_by(robot_user_id=robot_user_id, state='在线',is_delete=0).all()
        service_customer_id = None
        service_state_id = redis_store.get(uuid + 'customer_refresh')
        if service_state_id:
            customer_refresh = service_state_id.decode()
            service_state = CustomerService.query.filter_by(service_id=customer_refresh).first().state
            if service_state == '不在线':
                app_key = 'z3v5yqkbz1h60'
                app_secret = 'QASsvdjF7j'
                rcloud = RongCloud(app_key, app_secret)
                s = rcloud.User.checkOnline(userId=customer_refresh)
                # 在线状态，1为在线，0为不在线。
                if s.result['status'] == '1':
                    service_customer_id = customer_refresh
                    service = CustomerService.query.filter_by(robot_user_id=robot_user_id, is_delete=0).all()



        if not service:
            try:
                service_offline = CustomerService.query.filter_by(robot_user_id=robot_user_id, is_delete=0).first()
                result = {
                    "status": "200",
                    "msg": "not online",
                    "data": "您好，所有人工坐席不在线，您可以继续向机器人咨询，也可以拨打%s公司的客服热线：%s" % (service_offline.company, service_offline.service_hotline)
                }
                return jsonify(result)
            except Exception as e:
                current_app.logger.error(e)
                result = {
                    "status": "404",
                    "msg": "error",
                    "data": '数据库中没有此机器人对应的客服!'
                }
                return result
        li = []
        num = []
        for cs in service:
            li.append(cs.service_id)
            if redis_store.hget(redis_robot_service, cs.service_id) == None:
                redis_store.hset(redis_robot_service, cs.service_id, 0)
            num.append(int(redis_store.hget(redis_robot_service, cs.service_id).decode()))


        # 不能接入就排队
        byte_uuid = bytes(uuid, encoding='utf-8')
        line_number = redis_store.lrange(redis_robot_line, 0, -1)
        if min(num) >= 5:
            if byte_uuid in line_number:
                result = {
                    "status": "200",
                    "msg": "line",
                    "data": '客服繁忙,您前面还有%s人排队,请耐心等待' % (line_number.index(byte_uuid) + 1),
                    "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
                    "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
                }
                return result
            else:
                redis_store.rpush(redis_robot_line, uuid)
                line_number = redis_store.lrange(redis_robot_line, 0, -1)
                result = {
                    "status": "200",
                    "msg": "line",
                    "data": '客服繁忙,您前面还有%s人排队,请耐心等待' % (line_number.index(byte_uuid) + 1),
                    "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
                    "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
                }
                return result
        if min(num) < 5 and redis_store.llen(redis_robot_line) > 0:
            customer_redis_line = 'customer' + 'line' + str(robot_user_id)
            customer_get__line = redis_store.get(customer_redis_line)
            if not customer_get__line:
                redis_store.setex(customer_redis_line, 10, redis_store.lpop(redis_robot_line).decode())
            if byte_uuid == redis_store.get(customer_redis_line):
                redis_store.delete(customer_redis_line)
            # if byte_uuid == redis_store.lindex(redis_robot_line, 0):
            #    redis_store.lpop(redis_robot_line)
            else:
                if byte_uuid in line_number:
                    result = {
                        "status": "200",
                        "msg": "line",
                        "data": '客服繁忙,您前面还有%s人排队,请耐心等待' % (line_number.index(byte_uuid) + 1),
                        "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
                        "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
                    }
                    return result
                else:
                    redis_store.rpush(redis_robot_line, uuid)
                    line_number = redis_store.lrange(redis_robot_line, 0, -1)
                    result = {
                        "status": "200",
                        "msg": "line",
                        "data": '客服繁忙,您前面还有%s人排队,请耐心等待' % (line_number.index(byte_uuid) + 1),
                        "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
                        "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
                    }
                    return result
        service_mix_id = li[num.index(min(num))]

        # 如果该客户id30分钟之内再次访问,如果客户--客服,接待数量不超过5个接入
        if redis_store.get(uuid) and min(num) < 5 and redis_store.llen(redis_robot_line) == 0:
            try:
                customer_service = redis_store.get(uuid).decode()
                if num[li.index(customer_service)] < 5:
                    service_mix_id = customer_service
            except:
                service_mix_id = li[num.index(min(num))]

        if service_customer_id:
            service_mix_id = service_customer_id

        # 根据客户唯一id生成唯一客户token
        data = {}
        try:
            app_key = 'z3v5yqkbz1h60'
            app_secret = 'QASsvdjF7j'
            rcloud = RongCloud(app_key, app_secret)
            r = rcloud.User.getToken(userId=uuid, name=customer_name, portraitUri='')
            data['token'] = r.result['token']
        except Exception as e:
            current_app.logger.error(e)
            return {"status": "404", "msg": "error", "data": "token获取错误!"}
        data['user'] = customer_name
        try:
            data['targetId'] = service_mix_id
            data['welcome_words'] = '你好，我是人工客服%s，请问有什么可以帮助您？' % service[li.index(service_mix_id)].s_name
            robot_code = RobotSettings.query.filter_by(product_id=product_id, user_id=robot_user_id).first().robot_code + '机器人'
            product_name = Product.query.filter_by(id=product_id).first().display_name
            chat_log = AimiChatLogs.query.filter_by(dialog_id=uuid,service_user_id=None).order_by(AimiChatLogs.update_time,AimiChatLogs.role.desc()).all()
            chat_list = []
            for chat in chat_log:
                if chat.role == 'robot':
                    flag = 1
                elif chat.role == 'customer':
                    flag = 2
                else:
                    flag = 2
                chat_time = int(time.mktime(chat.create_time.timetuple()) * 1000)
                chat_list.append({'content': chat.content, 'sentTime': chat_time, 'messageDirection': flag})

            data['extra'] = [robot_code, product_name, chat_list, customer_name, product_id]
        except Exception as e:
            current_app.logger.error(e)
            return {"status": "404", "msg": "error", "data": "数据库查询错误,无此机器人对应客服!"}
        result = {
            "status": "200",
            "msg": "connect",
            "data": data,
            "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
            "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
        }
        return result


    # 排队请求
    def put(self):
        '''
        排队实现,判断机器人对应客户数,超过排队,列表append,如果机器人客户数不超过-->下一步,取出list[0]
        比对客户uuid和list,符合进入队列,list.index()判断位置,继续排队
        取消排队, redis结构 机器人--客户名称
        :return:
        '''
        usermessage = request.form
        uuid = usermessage.get('uuid', None)
        customer_name = usermessage.get('name', None)
        product_id = usermessage.get('product_id', None)
        robot_user_id = usermessage.get('robot_user_id', None)
        redis_robot_service = 'service' + str(robot_user_id)
        redis_robot_line = 'line' + str(robot_user_id)
        try:
            # redis_store.lrem(name, value, num)
            byte_uuid = bytes(uuid, encoding='utf-8')
            if byte_uuid in redis_store.lrange(redis_robot_line, 0, -1):
                redis_store.lrem(redis_robot_line, 0, byte_uuid)
                result = {
                    "status": "200",
                    "msg": "客户正在排队数量减少成功",
                    "data": uuid,
                    "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
                    "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
                }
                return result
        except Exception as e:
            current_app.logger.error(e)
            return {"status": "404", "msg": "error", "data": "客户正在排队数量减少错误!"}


class ConnectSuccess(Resource):
    def post(self):
        '''
        连接成功,客服对应客户数量加1
        redis 存储数据结构: 机器人_客服: [多客户]   机器人--客服--数量
        redis 客户对应客服编号
        机器人: [各客服数量]
        :return:
        '''
        usermessage = request.form
        uuid = usermessage.get('uuid', None)
        customer_name = usermessage.get('name', None)
        product_id = usermessage.get('product_id', None)
        robot_user_id = usermessage.get('robot_user_id', None)
        redis_robot_service = 'service' + str(robot_user_id)
        redis_robot_line = 'line' + str(robot_user_id)
        redis_status = 'status' + uuid
        service_id = usermessage.get('service_id',None)
        if not all([uuid, product_id, robot_user_id, service_id]):
            result = { "status": "404","msg": "error","data": "参数不完整"}
            return result
        redis_store.hincrby(redis_robot_service, service_id, amount=1)  # 机器人-客服id-客服接待人数
        redis_store.setex(uuid, 60*30, service_id)   # 客户--客服
        redis_store.set(redis_status, service_id)
        redis_store.set(uuid + 'customer_refresh', service_id)
        result = {
            "status": "200",
            "msg": "客服接待客户数增加成功",
            "data": service_id,
            "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
            "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
        }
        return result

class CustomerLogout(Resource):
    def post(self):
        '''
        根据service_id,redis客服相对应客户数量减1
        没有点取消排队,直接退出,没有传service_id的不减,减去redis中排队客户
        :return:
        '''
        usermessage = request.form
        uuid = usermessage.get('uuid', None)
        customer_name = usermessage.get('name', None)
        product_id = usermessage.get('product_id', None)
        robot_user_id = usermessage.get('robot_user_id', None)
        redis_robot_service = 'service' + str(robot_user_id)
        redis_robot_line = 'line'  + str(robot_user_id)
        service_id = usermessage.get('service_id', None)
        if not all([uuid, product_id, robot_user_id]):
            result = {"status": "404", "msg": "error", "data": "参数不完整"}
            return result
        try:
            if not service_id:
                # redis_store.lrem(name, value, num)
                byte_uuid = bytes(uuid, encoding='utf-8')
                if byte_uuid in redis_store.lrange(redis_robot_line, 0, -1):
                    redis_store.lrem(redis_robot_line, 0, byte_uuid)
                    result = {
                        "status": "200",
                        "msg": "客户正在排队数量减少成功",
                        "data": uuid,
                        "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
                        "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
                    }
                    return result
                else:
                    result = {
                        "status": "404",
                        "msg": "请传入service_id参数",
                        "data": uuid
                    }
                    return result
        except Exception as e:
            current_app.logger.error(e)
            return {"status": "404", "msg": "error", "data": "客户正在排队数量减少错误!"}
        redis_store.hincrby(redis_robot_service, service_id, amount=-1)
        if int(redis_store.hget(redis_robot_service,service_id).decode()) < 0:
            redis_store.hset(redis_robot_service, service_id, 0)
        result = {
            "status": "200",
            "msg": "客服接待客户数减少成功",
            "data": service_id,
            "redis_robot_line": str(redis_store.lrange(redis_robot_line, 0, -1)),
            "redis_robot_service": str(redis_store.hgetall(redis_robot_service))
        }
        return result


class CustomerSolve(Resource):
    def post(self):
        dialog_id = request.form.get('uuid', None)
        solve = request.form.get('solve', None)
        if not all([dialog_id, solve]):
            result = {"status": "404", "msg": "error", "data": "参数不完整"}
            return result
        try:
            chat_log = AimiChatLogs.query.filter(AimiChatLogs.dialog_id == dialog_id, AimiChatLogs.service_user_id > 0).all()
            for chat in chat_log:
                chat.solve = solve
                chat.save()
        except Exception as e:
            current_app.logger.error(e)
            return {"status": "404", "msg": "error", "data": "客户反馈增加错误!"}
        result = {
            "status": "200",
            "msg": "客服评价增加成功"
        }
        return result

