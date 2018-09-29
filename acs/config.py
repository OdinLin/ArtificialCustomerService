# coding:utf-8

import redis


# 配置信息
class Config(object):
    """开发环境与生产环境共有的配置信息"""
    SECRET_KEY = "DCHSODCYISxisuydfisu656fs*("

    # flask-session的配置信息
    SESSION_TYPE = "redis"  # 指明session数据保存在redis中
    SESSION_USE_SIGNER = True  # 指明对cookie中保存的session_id进行加密保护
    PERMANENT_SESSION_LIFETIME = 3 * 24 * 60 * 60  # session的有效，单位秒


class DevelopmentConfig(Config):
    """开发环境的配置信息"""
    DEBUG = True

    # 开发环境的数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/cms"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 开发环境的redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB = 10

    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)  # 使用的redis数据库


class ProductConfig(Config):

    """生产环境（线上环境）配置信息"""
    # 生产环境的数据库
    # 生产环境的redis
    DEBUG = True

    # 开发环境的数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:qbzz@2018@127.0.0.1:3306/cms"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 开发环境的redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB = 10

    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                                      db=REDIS_DB)
    pass


config_map = {
    "product": ProductConfig,
    "develop": DevelopmentConfig
}