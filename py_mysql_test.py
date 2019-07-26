# 引用pymysql模块
import pymysql
import logging

log_mysql = logging.getLogger("MySql")

# 连接mysql数据库，host等参数名字不可随意更改
conn = pymysql.connect(host="5780e03864e11.sh.cdb.myqcloud.com", port=4201, user="root", passwd="wlc570Q0", db="zhiyuan",charset="utf8")
# conn = pymysql.connect(host="134.175.87.30", port=3306, user="root", passwd="", db="test",charset="utf8")
print(conn)

def GetCityList(province:str):
    cur = conn.cursor()
    sql = 'SELECT `院校名称` FROM zy_data2018 WHERE `院校名称` = "浙江科技学院"'
    # sql = 'SELECT `院校名称`,`城市`,`省`,`本专科`,COUNT(`省`) AS count FROM zy_data2018 GROUP BY `院校名称` ORDER BY count DESC'

    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        # Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -100 Get user info failed sql语句错误
        return {"id": -1, "status": -100, "message": "Get record failed", "data": {}}
    print("num:{}".format(num))
    if num == 0:
        cur.close()
        # status 1 record is empty  记录不存在
        return {"id": -1, "status": 1, "message": "record is empty", "data": {}}
    else:
        rows = cur.fetchall()
        province_list = []

        for row in rows:
            province_list.append(row[0])
            # print(row[0])
        cur.close()
        # status 0 Successful 成功！
        print(province)
        return {"id": -1, "status": 0, "message": "Successful", "data": {"result": province_list, "type": "major"}}

if __name__ == '__main__':
    print(GetCityList("浙江"))
