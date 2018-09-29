from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
sess = Session()


def init_ext(app):

    db.init_app(app=app)
    db.app = app
    migrate.init_app(app=app,db=db)
    sess.init_app(app=app)

import redis

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 10
redis_store = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                                      db=REDIS_DB)


