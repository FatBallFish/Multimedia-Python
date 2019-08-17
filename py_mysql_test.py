# 引用pymysql模块
import pymysql
import logging

log_mysql = logging.getLogger("MySql")

# 连接mysql数据库，host等参数名字不可随意更改
conn = pymysql.connect(host="5780e03864e11.sh.cdb.myqcloud.com", port=4201, user="root", passwd="wlc570Q0", db="multimedia",charset="utf8")
# conn = pymysql.connect(host="134.175.87.30", port=3306, user="root", passwd="", db="test",charset="utf8")
print(conn)

def GetArticleList(keywords:str,article_id:int,title:str,content:str,order:str,start:int,num:int,id:int=-1)->dict:
    """
获取文章列表，
如果keywords不为空则优先使用keywords，article_id、title、content则被忽略；keywords用于title和content的并集查询，模糊匹配；
article_id、title、content可交集查询；
    :param keywords: 搜索关键字，设置后将以此关键字模糊匹配title和content字段内容
    :param article_id: 文章id，精确匹配
    :param title: 文章标题，模糊匹配
    :param content: 文章内容，模糊匹配
    :param order: 排序规则，使用SQL语句，为空则默认以更新时间进行排序
    :param start: 记录索引开始，默认起始为 0
    :param num: 返回记录数，默认返回50条
    :return: 返回json字典，包含id,status,message,data根字段
    """
    cur = conn.cursor()
    if order != "":
        order_list_first = order.split(",")
        for order_second in order_list_first:
            print("second:",order_second)
            order_list_second = order_second.split()
            order_third: str
            for order_third in order_list_second:
                print("third:", order_third)
                if order_third.lower() not in ["article_id", "user_id", "title", "content", "create_time", "update_time",
                                               "asc", "desc"]:
                    # status 100 Error Order 排序规则错误
                    return {"id": -1, "status": 100, "message": "Error Order", "data": {}}
        order = " ORDER BY " + order
    if num <= 0 :
        # status 101 Error num num值错误
        return {"id":id,"status":101,"message":"Error num","data":{}}


    if keywords != "":
        sql = "SELECT * FROM bbs_article WHERE title LIKE '%{0}%' OR content LIKE '%{0}%' {1} LIMIT {2} , {3}".format(
            keywords, order, start, num)
    else:
        condition = ""
        if article_id != 0:
            condition = condition + "article_id = {} AND ".format(article_id)
        if title != "":
            condition = condition + "title LIKE '%{}%' AND ".format(title)
        if content != "":
            condition = condition + "content LIKE '%{}%' AND ".format(content)

        if condition == "":
            sql = "SELECT * FROM bbs_article {0} LIMIT {1} , {2}".format(order, start, num)
        else:
            condition = condition.rpartition("AND ", )[0]
            sql = "SELECT * FROM bbs_article WHERE {} {} LIMIT {} , {}".format(condition, order, start, num)
    print(sql)
    try:
        row_num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        # Auto_KeepConnect()
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

    rows = cur.fetchall()
    cur.close()
    # row_num = len(rows)
    if row_num == 0:
        # status 0 successful
        return {"id":id,"status":0,"message":"successful","data":{"num":0,"list":[]}}
    article_list = []
    article_dict = {}
    for row in rows:
        article_dict["article_id"] = row[0]
        article_dict["user_id"] = row[1]
        article_dict["title"] = row[2]
        article_dict["content"] = row[3]
        article_dict["create_time"] = str(row[4])
        article_dict["update_time"] = str(row[5])
        article_list.append(article_dict)
    # status 0 successful
    return {"id": id, "status": 0, "message": "successful", "data": {"num": row_num, "list": article_list}}

if __name__ == '__main__':
    keywords = ""
    article_id = 1565926081
    title = "测试"
    content = "文章"
    order = "update_time DESC"
    # order = "create_time ASC,title DESC"
    start = 0
    num = 1
    print(GetArticleList(keywords=keywords,article_id=article_id,title=title,content=content,order=order,start=start,num=num))
