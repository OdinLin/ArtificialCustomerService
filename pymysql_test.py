# -*- coding:utf-8 -*-
__author__ = 'Roy'
__date__ = '2018/9/29 10:48'

import pymysql

connection = pymysql.connect(host='127.0.0.1', user='root', password="123456",
                 database='cms', port=3306, db='python',charset='utf8')

with connection.cursor() as cursor:
    sql = 'select robot_user_id, service_id from customer_service where service_id = "%s" and is_delete=0' % ('9nFLC7/RgbIIEBlqQ5xG/FfbRjwhmykJ5L0M1IUIFLvvG2mlhMscjuxHzmhaiPsgxjlztR5k7RiFQl/qDVbHpdlgKvfJ1WzDjUoy2e4vKf1YKOXadmCSReopg61DFsrU')
    cursor.execute(sql)
    results = cursor.fetchone()
    robot_user_id = results[0]
    print(robot_user_id)
    cursor.execute('update customer_service set state = "%s" where id = 1' % ('不在线'))
    print(results)
    connection.commit()