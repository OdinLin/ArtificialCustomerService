# -*- coding:utf-8 -*-

from acs.utils.db_model import Addmodel
from acs.ext import db
from werkzeug import security
from datetime import datetime


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now,
                            onupdate=datetime.now)  # 记录的更新时间


class CustomerService(Addmodel, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    s_name = db.Column(db.String(32),nullable=False,comment='客服昵称')
    identity = db.Column(db.Enum("admin","service"), default='service')
    mobile = db.Column(db.String(11),nullable=False, comment='客服手机号')
    company = db.Column(db.String(128),nullable=False, comment='公司名')
    service_hotline = db.Column(db.String(32),nullable=False,comment='公司客户热线')
    service_id = db.Column(db.String(128), nullable=False,comment='客服通信id(md5主键),用于token等')
    password_hash = db.Column(db.String(128),nullable=False,comment='hash加密密码')
    s_token = db.Column(db.String(256),comment='客服token')
    # product_id = db.Column(db.Integer,nullable=False,comment='关联产品表')
    robot_user_id = db.Column(db.Integer,nullable=False,comment='关联机器人用户id')
    state = db.Column(db.Enum("在线","不在线"),comment='客服状态')
    is_delete = db.Column(db.Integer, nullable=False, default=0, comment='是否删除0:没有删除, 1:已删除')

    def check_password(self, origin_password):
        """检验用户的密码是否正确
        : param origin_password:  用户登录时输入的原始密码
        """
        return security.check_password_hash(self.password_hash, origin_password)

    @property
    def password(self):
        """
        对应额外添加的属性password的读取行为
        :return:
        """
        # 在我们这个应用场景中，读取密码没有实际意义
        # 所以对于password属性的读取行为的函数不再实现
        # 通常以抛出AttributeError的方式来作为函数代码
        raise AttributeError("不支持读取操作")

    @password.setter
    def password(self, origin_password):
        """
        对应额外添加的属性password的设置行为
        """
        self.password_hash = security.generate_password_hash(origin_password)


class AimiChatLogs(Addmodel,BaseModel, db.Model):
    """对话历史"""

    __tablename__ = "chat_logs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    role = db.Column(db.Enum("robot", "customer", "service"), nullable=False, index=True)
    dialog_id = db.Column(db.String(128), nullable=False, default="")  # 归属地的区域编号
    user_id = db.Column(db.Integer, nullable=False, comment="关联user表key")
    product_id = db.Column(db.Integer, comment="管理product表的key")
    content = db.Column(db.String(256), nullable=False)  # 标题
    is_solve = db.Column(db.Enum("未选", "已解决",  "未解决",), default="未选", index=True)
    robot_code = db.Column(db.String(32), nullable=False, default="001", comment="机器人编号")
    service_user_id = db.Column(db.Integer, nullable=False, comment="客服id")


    def to_dict(self):
        """将基本信息转换为字典数据"""
        st_create_time = self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        log_dict = {
            "id": self.dialog_id,
            "create": st_create_time,
            "role": self.role,
            "name": self.name,
            "content": self.content,
            "is_solve": self.is_solve,
            "robot_code":self.robot_code
        }
        return log_dict


class RobotSettings(BaseModel, db.Model):
    """机器人设置"""

    __tablename__ = "robot_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer , nullable=False, comment="关联user表的key")  # 区域的房屋
    product_id = db.Column(db.Integer, nullable=False, comment="关联product表的key")
    welcome_words = db.Column(db.String(256), default="您好,我是Aimi,欢迎咨询")
    wait_words = db.Column(db.String(256), default="让我思考一下哦~")
    timeout_words = db.Column(db.String(256), default="亲,因为您很久没有理Aimi了,我先去玩儿啦,有事再叫我~")
    app_id = db.Column(db.String(32))
    api_key = db.Column(db.String(128))
    secret_key = db.Column(db.String(128))
    robot_name = db.Column(db.String(128))
    robot_type = db.Column(db.String(128))
    picture = db.Column(db.String(128))
    robot_code = db.Column(db.String(32),nullable=False,default="001",comment="机器人编号")
    deployment_form = db.Column(db.Enum("H5", "API"), nullable=False, default="H5", comment="部署形式")
    comment = db.Column(db.String(300), default="", comment="机器人备注")
    uri = db.Column(db.String(32), nullable=False, default="dybz2018", comment="机器人链接地址")
    def to_dict(self):
        """将对象转换为字典"""
        d = {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "welcome_words": self.welcome_words,
            "wait_words": self.wait_words,
            "timeout_word": self.timeout_words,
            "name":self.robot_name,
            "type":self.robot_type,
            "robot_code": self.robot_code,
            "deployment_form": self.deployment_form,
            "comment": self.comment,
            "uri": self.uri
        }
        return d


class Product(BaseModel, db.Model):
    """订单"""

    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)  # 订单编号
    code = db.Column(db.String(32), nullable=False, default="", comment="机器人编码")
    name = db.Column(db.String(64), nullable=False, default="", comment="机器人名称")
    display_name = db.Column(db.String(64), nullable=False, default="", comment="显示名称")
    url = db.Column(db.String(128), nullable=False, default="", comment="机器人服务器地址")
    insurance_company = db.Column(db.String(128), nullable=False)
    insurance_product = db.Column(db.String(128), nullable=False)
    policy_id = db.Column(db.Integer, nullable=False, default=0)
    policy_type = db.Column(db.Integer, nullable=False, default=1)


class RobotService(Addmodel, db.Model):
    """机器人对应客服表"""
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)   #
    user_id = db.Column(db.Integer, nullable=False, comment="关联user表key")
    product_id = db.Column(db.Integer, comment="管理product表的key")
    service_user_id = db.Column(db.Integer, nullable=False, comment="客服id")
    robot_code = db.Column(db.String(32), nullable=False, default="001", comment="机器人编号")
    is_delete = db.Column(db.Integer, nullable=False, default=0, comment='是否删除0:没有删除, 1:已删除')


class DataPlan(Addmodel, db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    month_balance = db.Column(db.Integer)               # 月度流量余额
    month_expiration_time = db.Column(db.String(32))      # 月度过期时间
    month_free = db.Column(db.Integer)       # 月度免费次数
    year_balance = db.Column(db.Integer)                # 年度流量余额
    year_expiration_time = db.Column(db.String(32))       # 年度过期时间
    user_id = db.Column(db.Integer, nullable=False)
    month_fixation_update = db.Column(db.Integer, nullable=False, default=1000, comment='月度免费流量固定更新条数')