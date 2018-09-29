from acs import create_app
from flask_migrate import MigrateCommand
from flask_script import Manager

# 创建flask工程应用对象
app = create_app("develop")
# app = create_app("product")


# 启动命令扩展
manager = Manager(app)


# 添加数据库迁移命令
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    # manager.run()
    app.run(host="0.0.0.0", port=8888, debug=False)
