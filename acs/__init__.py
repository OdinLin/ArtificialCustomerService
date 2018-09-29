# -*- coding:utf-8 -*-

from flask import Flask
from acs.ext import init_ext
from acs.apis import init_api
from acs.config import config_map
import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS


# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级

# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs\log", maxBytes=1024 * 1024 * 100, backupCount=10)

# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)

# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)


# 工厂模式
def create_app(run_name):
    """工厂函数，用来创建flask应用对象
    :param run_name: flask运行的模式名字， product-生产模式  develop-开发模式
    """
    app = Flask(__name__)
    app.config.from_object(config_map.get(run_name))



    CORS(app, resources=r'/*') # 允许所有url跨域

    # 注册 扩展库
    init_ext(app)
    # create_app(app)


    # restful api
    init_api(app)

    return app