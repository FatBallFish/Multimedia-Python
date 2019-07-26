# 引用pymysql模块
import pymysql
import logging

log_mysql = logging.getLogger("MySql")

# 连接mysql数据库，host等参数名字不可随意更改
conn = pymysql.connect(host="5780e03864e11.sh.cdb.myqcloud.com", port=4201, user="root", passwd="wlc570Q0", db="zhiyuan",charset="utf8")
# conn = pymysql.connect(host="134.175.87.30", port=3306, user="root", passwd="", db="test",charset="utf8")
print(conn)

def f():
    cur = conn.cursor()
    sql = 'SELECT `院校名称` FROM zy_data2018 WHERE `学制`="" GROUP BY `院校名称`'
    # sql = 'SELECT `院校名称`,`城市`,`省`,`本专科`,COUNT(`省`) AS count FROM zy_data2018 GROUP BY `院校名称` ORDER BY count DESC'
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        # status -100 Get user info failed sql语句错误
        return {"id": -1, "status": -100, "message": "Get record failed", "data": {}}
    if num == 0:
        cur.close()
        # status 1 record is empty  记录不存在
        return {"id": -1, "status": 1, "message": "record is empty", "data": {}}
    else:
        rows = cur.fetchall()
        cur.close()
        school_list = []
        for row in rows:
            # print(row)

            school = row[0]
            # print(school)
            cur = conn.cursor()
            sql = 'SELECT `院校名称`,`学制`,`本专科` FROM zy_data2018 WHERE `学制`<>"" AND `院校名称`="{}" LIMIT 1'.format(school)
            num = cur.execute(sql)
            conn.commit()
            row2 = cur.fetchone()
            if row2 == None:
                print("无任何信息：",school)
                continue
            # print(row2)
            cur.close()
            # print(row2[1],row2[2])
            year = row2[1]
            position = row2[2]

            cur = conn.cursor()
            sql = 'UPDATE zy_data2018 SET `学制`= "{}",`本专科` = "{}" WHERE `院校名称` = "{}"'.format(year,position,school)
            num = cur.execute(sql)
            conn.commit()
            cur.close()
            school_list.append(row[0])




        # status 0 Successful 成功！
        return {"id": -1, "status": 0, "message": "Successful", "data": {"result": school_list, "type": "major"}}

    # 关闭数据库连接
    conn.close()

if __name__ == '__main__':
    print(f())
