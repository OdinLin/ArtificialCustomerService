# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/9/7 9:16'

from flask import g, request, current_app, jsonify, session
from flask_restful import Resource, fields, marshal
from acs.utils.commons import login_required
from acs.models import CustomerService
from acs.ext import redis_store
import re, random
from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient


resource_fields = {
    'id': fields.Integer,
    's_name': fields.String,
    'identity': fields.String,
    'mobile': fields.String,
    'company': fields.String,
    'service_hotline': fields.String,
    's_token': fields.String,
    'state': fields.String,
}

resources_fields = {
    'status': fields.String,
    'msg': fields.String,
    'data':fields.Nested(resource_fields)
}

class GetUseInfo(Resource):
    @login_required
    def get(self):
        """获取客服信息"""
        user_id = g.user_id
        try:
            user = CustomerService.query.filter_by(id=user_id, is_delete=0).first()
            redis_store.set('repeat_login' + user.service_id, 1)
        except Exception as e:
            current_app.logger.error(e)
            result = {
                "status": "404",
                "msg": "error",
                "data": '获取用户信息失败'
            }
            return result

        result = {
            "status": "200",
            "msg": "ok",
            "data": user
        }
        return marshal(result, resources_fields)




class ResetPassword(Resource):
    @login_required
    def post(self):
        req_dict = request.form
        mobile = req_dict.get("mobile", None)
        sms_code = req_dict.get("sms_code", None)
        password = req_dict.get("password", None)
        password2 = req_dict.get("password2", None)

        # 校验参数
        if not all([mobile, sms_code, password, password2]):
            return jsonify(errcode="404", errmsg="参数不完整")

        # 判断密码一致
        if password != password2:
            return jsonify(errcode="404", errmsg="两次密码不一致")

        # 从redis中获取短信验证码的真实值
        try:
            real_sms_code = redis_store.get("sms_code_%s" % mobile)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode="404", errmsg="数据库异常")

        # 判断验证码是否过期
        if real_sms_code is None:
            return jsonify(errcode="404", errmsg="短信验证码已过期")

        # 与用户填写的短信验证码进行对比
        if int(real_sms_code) != int(sms_code):
            return jsonify(errcode="404", errmsg="短信验证码错误")

        try:
            user = CustomerService.query.filter_by(mobile=mobile,is_delete=0).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode="404", errmsg="数据库异常")
        try:
            user.password = password # 设置属性
            user.save()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode="404", errmsg="保存用户信息异常")

        # 用session保存登录状态
        session["user_id"] = user.id
        session["mobile"] = mobile
        session["user_name"] = mobile

        # 返回注册成功的信息
        return jsonify(errcode="200", errmsg="修改密码成功", data={"user_id": user.id})





class ServiceLogin(Resource):
    def post(self):
        """登录"""

        # 获取参数  手机号、密码
        req_dict = request.form
        if req_dict == None:
            return jsonify(errcode="404", errmsg="数据类型错误")
        mobile = req_dict.get("mobile",None)
        password = req_dict.get("password",None)

        # 校验参数
        if not all([mobile, password]):
            return jsonify(errcode="404", errmsg="参数不完整")


        if not re.match(r"1[3456789]\d{9}", mobile) and mobile != "00000000000":
            return jsonify(errcode="404", errmsg="手机号格式错误")

        # 根据请求用户的ip地址，读取他的错误次数， redis
        user_ip = request.remote_addr  # 请求用户的ip地址
        try:
            wrong_access_num = redis_store.get("access_num_%s" % user_ip)
        except Exception as e:
            current_app.logger.error(e)
        else:
            # 判断这个ip地址的错误尝试次数
            if wrong_access_num is not None and int(wrong_access_num) >= 10:
                # 如果错误次数超过限制，则直接返回
                return jsonify(errcode="404", errmsg="错误次数过多，请稍后再试")

        # 如果未超过限制，验证手机号与密码
        # 根据手机号从数据库中取出用户的真实加密密码，对用户的登录输入密码进行加密计算，比较两个值，
        try:
            user = CustomerService.query.filter_by(mobile=mobile,is_delete=0).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode="404", errmsg="数据库异常")

        if user is None or not user.check_password(password):
            # 表示用户的手机号错误   密码错误
            # 否则登录失败， 保存记录错误次数  "access_num_ip地址": "错误次数" 字符串类型
            # 如果用户是第一次错误尝试，redis中保存数据1
            # 如果不是第一次错误，redis中的数据需要累加1
            try:
                redis_store.incr("access_num_%s" % user_ip)
                redis_store.expire("access_num_%s" % user_ip, 600)
            except Exception as e:
                current_app.logger.error(e)
            return jsonify(errcode="404", errmsg="用户名或密码错误")

        # 如果相同，登录成功，保存登录状态
        # 用session保存登录状态
        if redis_store.get('repeat_login'+user.service_id):
            result = {
                "status": "200",
                "msg": "重复登录",
                "data": '您的账号已在其他地方登录,请勿重复登录!'
            }
            return result
        redis_store.set('repeat_login'+user.service_id, 1)
        session["user_id"] = user.id
        session["mobile"] = mobile
        session["user_name"] = user.s_name
        result = {
            "status": "200",
            "msg": "登录成功",
            "data": user
        }
        return marshal(result, resources_fields)

    @login_required
    def delete(self):
        """登出"""
        # 清除session数据
        user_id = g.user_id
        service = CustomerService.query.filter_by(id=user_id, is_delete=0).first()
        service.state = "不在线"
        service.save()
        redis_store.delete('repeat_login' + service.service_id)
        redis_robot_service = 'service' + str(service.robot_user_id)
        redis_robot_line = 'line' + str(service.robot_user_id)
        # redis_store.hincrby(redis_robot_service, service_id, amount=1)
        redis_store.hset(redis_robot_service, service.service_id, 0)
        # 如果所有客服都不在线,清空列表和客服接待数量
        # #移除列表内没有在该索引之内的值r.ltrim("list_name",0,2)
        all_service = CustomerService.query.filter_by(robot_user_id=service.robot_user_id, state='在线',is_delete=0).all()
        if not all_service:
            all_service = CustomerService.query.filter_by(robot_user_id=service.robot_user_id,is_delete=0).all()
            for service in all_service:
                redis_store.hset(redis_robot_service, service.service_id, 0)
            redis_store.ltrim(redis_robot_line, 0, 0)  #移除列表内没有在该索引之内的值
            redis_store.lrem(redis_robot_line, 0, redis_store.lindex(redis_robot_line, 0)) # 移除指定位置索引
            pass
        session.clear()
        return jsonify(errcode="200", errmsg="OK")


class SendSmsCode(Resource):
    @login_required
    def get(self):
        """发送短信验证码"""
        mobile = request.args.get('mobile')
        if not re.match(r"1[3456789]\d{9}", mobile) and mobile != "00000000000":
            return jsonify(errcode="404", errmsg="手机号格式错误")
        try:
            flag = redis_store.get("send_sms_code_flag_%s" % mobile)
        except Exception as e:
            current_app.logger.error(e)
        else:
            if flag is not None:
                # 表示2分钟有发送记录
                return jsonify(errcode="404", errmsg="发送过于频繁")

        # 生成短信验证码
        # %06d表示格式化显示，至少6位数字，不足6位前面补0
        sms_code = "%06d" % random.randint(0, 999999)

        # 保存手机号和短信验证码
        try:
            redis_store.setex("sms_code_%s" % mobile, 60 * 2, sms_code)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode="404", errmsg="保存短信验证码异常")

        # 保存发送的记录到redis中
        try:
            redis_store.setex("send_sms_code_flag_%s" % mobile, 60 * 2, 1)
        except Exception as e:
            current_app.logger.error(e)
        mobile = str(mobile)
        apikey = "430c6711eff8790f8d9d9ca4849bf6bd"
        clnt = YunpianClient(apikey)
        # mobile = str(mobile)
        param = {YC.MOBILE: mobile, YC.TEXT: '【企保科技】您的验证码是%s' % sms_code}
        r = clnt.sms().single_send(param)
        if r.code() == 0:
            return jsonify(errcode="200", errmsg="发送成功")
        else:
            return jsonify(errcode="404", errmsg="发送失败,请稍后重试")





