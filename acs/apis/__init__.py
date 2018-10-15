# -*- coding:utf-8 -*-

from flask_restful import Api
from acs.apis.customer import CustomerLogin, ConnectSuccess, CustomerLogout, CustomerSolve
from acs.apis.service_passport import GetUseInfo, ResetPassword, SendSmsCode, ServiceLogin
from acs.apis.service import ChangeServiceState, ServiceShutWeb, MessageRoute, ServiceOnlineStatus
from acs.apis.service_record import RobotNumber, ServiceNumber, RecordDialogs, RecordExcel
from acs.apis.service_robot_answer import RobotAnswer, RobotBalance





api = Api()

def init_api(app):
    api.init_app(app=app)


# 客户页面(登录,连接成功,注销)参数都是:uuid,name(客户名),product_id(产品id),robot_user_id(用户id)
api.add_resource(CustomerLogin,'/acs/v1.0/customer_login') # post请求:登录, put请求:取消排队
api.add_resource(ConnectSuccess,'/acs/v1.0/customer_connect_success') # post请求 连接成功后调用  service_id
api.add_resource(CustomerLogout,'/acs/v1.0/customer_logout') # post请求:点击退出人工客服按钮,调用, service_id
api.add_resource(CustomerSolve,'/acs/v1.0/customer_solve') # post请求,客服是否解决评价,参数:uuid, solve

# 客服信息,登录,重置密码,发送短信等
api.add_resource(GetUseInfo,'/acs/v1.0/service_message')  # get请求获取客服信息,无参数
api.add_resource(ResetPassword,'/acs/v1.0/reset_password') # post请求重置密码,(mobile,sms_code,password,password2)
api.add_resource(SendSmsCode,'/acs/v1.0/send_code')  # get请求发送验证码,参数:mobile
api.add_resource(ServiceLogin,'/acs/v1.0/service_login') # post客服登录(mobile,password),delete客服注销(无参数)

# 客服聊天(状态,会话)
api.add_resource(ChangeServiceState,'/acs/v1.0/change_service_state') # post请求变更客服状态,参数是state(在线,不在线)
api.add_resource(ServiceShutWeb,'/acs/v1.0/service_shut_web') # post请求,将客服状态变更为不在线,客服接待数量变为0
api.add_resource(MessageRoute,'/acs/v1.0/message_route') # 实时消息路由
api.add_resource(ServiceOnlineStatus,'/acs/v1.0/service_online_status') # 在线状态订阅




# 客服历史对话页面
api.add_resource(RobotNumber,'/acs/v1.0/robot_number')  # get请求,机器人编号
api.add_resource(ServiceNumber,'/acs/v1.0/service_number') # get请求,客服名
api.add_resource(RecordDialogs,'/acs/v1.0/record_dialogs') # get获取历史对话信息 role(客服id),start_date,end_date,p,robot_code
api.add_resource(RecordExcel,'/acs/v1.0/record_excel') # 获取excel历史对话信息,role,start_date,end_date,robot_code


# 客户机器人回答
api.add_resource(RobotAnswer,'/acs/v1.0/robot_answer') # post请求 参数:sentence,dialogId,productId,customer_name
api.add_resource(RobotBalance,'/acs/v1.0/robot_balance') # post请求 参数:sentence,robot_answer,dialogId,productId,customer_name


