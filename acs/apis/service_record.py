# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/9/7 14:08'

from flask import g, request, jsonify, current_app, make_response, send_from_directory
from flask_restful import Resource, fields, marshal
from acs.utils.commons import login_required
from acs.models import AimiChatLogs, RobotSettings, CustomerService, RobotService
import datetime, os, xlwt
from sqlalchemy import or_

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


class RecordDialogs(Resource):
    @login_required
    def get(self):
        user_id = g.user_id
        args_dict = request.args
        role = args_dict.get("role", None)
        start_date = args_dict.get("start_date", None)
        end_date = args_dict.get("end_date",None)
        page = args_dict.get("p", "1")
        robot_code = args_dict.get("robot_code", None)
        try:
            page = int(page)
        except Exception as e:
            current_app.logger.error(e)
            page = 1
        # chat_user_id = CustomerService.query.filter_by(id=user_id).first().robot_user_id
        filter_params = []
        # filter_params.append(AimiChatLogs.user_id == chat_user_id)
        # filter_params.append(AimiChatLogs.service_user_id > 0)
        # filter_params.append(AimiChatLogs.service_user_id == user_id)
        chatlogs = AimiChatLogs.query.filter(AimiChatLogs.service_user_id == user_id).all()
        all_dialog = []
        for dialog in chatlogs:
            all_dialog.append(dialog.dialog_id)
        filter_params.append(or_(AimiChatLogs.service_user_id == user_id,AimiChatLogs.dialog_id.in_(all_dialog)))
        if robot_code:
            filter_params.append(AimiChatLogs.robot_code == robot_code)
        if role:
            filter_params.append(AimiChatLogs.role == role)
        if start_date:
            st_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            filter_params.append(AimiChatLogs.create_time>=st_start_date)
        if end_date:
            st_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            filter_params.append(AimiChatLogs.create_time<=st_end_date)
        try:
            query = AimiChatLogs.query.filter(*filter_params).order_by(AimiChatLogs.id.desc(),AimiChatLogs.role)
            total_num = AimiChatLogs.query.filter(*filter_params).count()
            if query:
                page_obj = query.paginate(page,per_page=10,error_out=False)
            else:
                return jsonify(errcode="404", errmsg="没有相关记录")
        except Exception as e:
            current_app.logger.error(e)
            # return jsonify(errcode="404", errmsg='数据库查询异常')
        else:
            logs = page_obj.items
            total_page = page_obj.pages
            logs_dict_list = []
            if logs:
                for log in logs:
                    log_dict = log.to_dict()
                    if log_dict['is_solve'] == '未选' or log_dict['is_solve'] == None:
                        log_dict['is_solve'] = '无反馈'
                    logs_dict_list.append(log_dict)
            return jsonify(errcode='200', errmsg="OK",
                           data={"log_dict_list":logs_dict_list,
                                 "total_page": total_page, "total_num": total_num,"current_page": page})

class RecordExcel(Resource):
    @login_required
    def get(self):
        user_id = g.user_id
        args_dict = request.args
        role = args_dict.get("role", None)
        start_date = args_dict.get("start_date", None)
        end_date = args_dict.get("end_date", None)
        robot_code = args_dict.get("robot_code", None)
        # chat_user_id = CustomerService.query.filter_by(id=user_id).first().robot_user_id
        filter_params = []
        # filter_params.append(AimiChatLogs.user_id == chat_user_id)
        # filter_params.append(AimiChatLogs.service_user_id > 0)
        chatlogs = AimiChatLogs.query.filter(AimiChatLogs.service_user_id == user_id).all()
        all_dialog = []
        for dialog in chatlogs:
            all_dialog.append(dialog.dialog_id)
        filter_params.append(or_(AimiChatLogs.service_user_id == user_id, AimiChatLogs.dialog_id.in_(all_dialog)))
        if robot_code:
            filter_params.append(AimiChatLogs.robot_code == robot_code)
        if role:
            filter_params.append(AimiChatLogs.role == role)
        if start_date:
            st_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            filter_params.append(AimiChatLogs.create_time >= st_start_date)
        if end_date:
            st_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            filter_params.append(AimiChatLogs.create_time <= st_end_date)
        try:
            logs = AimiChatLogs.query.filter(*filter_params).order_by(AimiChatLogs.id.desc(),
                                                                      AimiChatLogs.role).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode="404", errmsg='数据库查询异常')
        else:
            filename = os.path.abspath("./log_csv/log.xls")
            wb = xlwt.Workbook(encoding='ascii')
            ws = wb.add_sheet('qb',cell_overwrite_ok=True)
            i = 1
            head = ["对话组ID", "机器人编号", "时间", "角色", "名称", "内容", "用户反馈"]
            ws.write(0, 0, label=head[0])
            ws.write(0, 1, label=head[1])
            ws.write(0, 2, label=head[2])
            ws.write(0, 3, label=head[3])
            ws.write(0, 4, label=head[4])
            ws.write(0, 5, label=head[5])
            ws.write(0, 6, label=head[6])
            for log in logs:
                dialog_id = log.dialog_id
                robot_code = log.robot_code
                time = log.create_time.strftime("%Y-%m-%d %X")
                role = log.role
                name = log.name
                content = log.content
                solve = log.is_solve
                if solve == '未选' or solve == None:
                    solve = '无反馈'
                ws.write(i, 0, label=dialog_id)
                ws.write(i, 1, label=robot_code)
                ws.write(i, 2, label=time)
                ws.write(i, 3, label=role)
                ws.write(i, 4, label=name)
                ws.write(i, 5, label=content)
                ws.write(i, 6, label=solve)
                i += 1
            wb.save('./record_excel/history.xls')
            filename = os.path.abspath("./record_excel")
            response = make_response(send_from_directory(filename, "history.xls",
                                                         as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(
                "history.xls".encode().decode('latin-1'))
            response.headers["Content-Type"] = "application/vnd.ms-excel"
            return response
            # return send_from_directory(filename, "log.csv", as_attachment=True)

class RobotNumber(Resource):
    @login_required
    def get(self):
        user_id = g.user_id
        robot_num = RobotService.query.filter_by(service_user_id=user_id).all()
        robot_list = []
        for i in robot_num:
            robot_list.append(i.robot_code)
        result = {
            "status": "200",
            "msg": "机器人编号",
            "data": robot_list
        }
        return result

class ServiceNumber(Resource):
    '''此代码获取所有客服信息,已更改需求,无任何用途'''
    @login_required
    def get(self):
        user_id = g.user_id
        robot_user = CustomerService.query.filter_by(id=user_id,is_delete=0).first().robot_user_id
        service_num = CustomerService.query.filter_by(robot_user_id=robot_user,is_delete=0).all()
        result = {
            "status": "200",
            "msg": "客服名",
            "data": service_num
        }
        return marshal(result, resources_fields)
