# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/9/20 10:54'


from flask import g, request, jsonify, current_app
from flask_restful import Resource, fields, marshal
from acs.utils.commons import login_required
from acs.models import Product, DataPlan, AimiChatLogs, RobotSettings, CustomerService
import requests



class RobotAnswer(Resource):
    # 机器人答案
    @login_required
    def post(self):
        sentence = request.form.get('sentence', None)   # 监听content
        '''dialogId=targetId'''
        dialogId = request.form.get('dialogId', None)   # 监听userid(uuid)
        productId = request.form.get('productId', None)
        serviceId = g.user_id

        customer_name = request.form.get('customer_name', None)

        if not all([dialogId, productId, serviceId, sentence]):
            result = {"status": "404", "msg": "error", "data": "参数不完整"}
            return result
        try:
            custom_service = CustomerService.query.filter_by(id=serviceId, is_delete=0).first()
            userId = custom_service.robot_user_id
            product_message = Product.query.filter_by(id=productId).first()
            policyId = product_message.policy_id
            policyType = product_message.policy_type
            product_url = product_message.url
            robot_request={}
            robot_request['sentence'] = sentence
            robot_request['dialogId'] = dialogId
            robot_request['policyId'] = policyId
            robot_request['policyType'] = policyType
            robot_request['productId'] = productId
            robot_request['userId'] = userId
        except Exception as e:
            current_app.logger.error(e)
            result = {"status": "404", "msg": "error", "data": "数据库信息查询错误"}
            return result
        try:
            data_balance = DataPlan.query.filter_by(user_id=userId).first()
            month_balance = data_balance.month_balance
            year_balance = data_balance.year_balance
            if (month_balance or year_balance) > 0:
                '''post请求机器人接口'''
                robot_answer = requests.post(product_url, data=robot_request)
                '''机器人接口返回json数据格式'''
                '''{'message':{'data':['111', '222', '333'], 'select':['666', '777', '888']}}'''
            else:
                result = {"status": "200", "msg": "用户流量余额已不足,请及时充值", "data": "您好,机器人正在休息了呢,请与我们的人工客服联系哦"}
                return result
        except Exception as e:
            current_app.logger.error(e)
            result = {"status": "404", "msg": "error", "data": "机器人接口获取消息错误"}
            return result
        data = {}
        data['userId'] = userId
        data['productId'] = productId
        data['dialogId'] = dialogId
        data['robot_answer'] = robot_answer.json() # 机器人接口数据返回类型
        data['sentence'] = sentence
        data['customer_name'] = customer_name
        result = {
            "status": "200",
            "msg": "机器人返回信息",
            "data": data
        }
        return result


class RobotBalance(Resource):
    # 机器人流量扣除, 消息保存
    @login_required
    def post(self):
        serviceId = g.user_id
        sentence = request.form.get('sentence', None)
        robot_answer = request.form.get('robot_answer', None)
        '''dialogId=targetId'''
        dialogId = request.form.get('dialogId', None)
        productId = request.form.get('productId', None)

        customer_name = request.form.get('customer_name', None)

        custom_service = CustomerService.query.filter_by(id=serviceId, is_delete=0).first()
        if not all([dialogId, productId, custom_service, sentence, robot_answer]):
            result = {"status": "404", "msg": "error", "data": "参数不完整"}
            return result
        try:
            data_balance = DataPlan.query.filter_by(user_id=custom_service.robot_user_id).first()
            month_balance = data_balance.month_balance
            year_balance = data_balance.year_balance
            if month_balance > 0:
                month_balance -= 1
            elif year_balance > 0:
                year_balance -= 1
            else:
                result = {"status": "200", "msg": "用户流量余额已不足,请及时充值", "data": "您好,机器人正在休息了呢,请与我们的人工客服联系哦"}
                return result
            data_balance.save()
            robot_message = RobotSettings.qurey.filter_by(user_id=custom_service.robot_user_id, product_id=productId).first()
            '''customer问题'''
            chat_log = AimiChatLogs(name=customer_name, role='customer', dialog_id=dialogId,
                                    user_id=custom_service.robot_user_id, product_id=productId, content=sentence,
                                    robot_code=robot_message.robot_code)
            chat_log.save()
            '''robot答案'''
            chat_log2 = AimiChatLogs(name=robot_message.robot_name, role='robot', dialog_id=dialogId,
                                     user_id=custom_service.robot_user_id, product_id=productId, content=robot_answer,
                                     robot_code=robot_message.robot_code)
            chat_log2.save()
            result = {
                "status": "200",
                "msg": "机器人流量扣除,历史对话增加",
                "data": '机器人流量扣除成功,历史对话增加成功'
            }
            return result
        except:
            result = {"status": "404", "msg": "error", "data": "数据库中没有此机器人对应流量套餐信息"}
            return result




