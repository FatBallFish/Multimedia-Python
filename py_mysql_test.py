# 引用pymysql模块
import pymysql
import logging
import MD5,time

log_mysql = logging.getLogger("MySql")

# 连接mysql数据库，host等参数名字不可随意更改
conn = pymysql.connect(host="5780e03864e11.sh.cdb.myqcloud.com", port=4201, user="root", passwd="wlc570Q0", db="multimedia",charset="utf8")
# conn = pymysql.connect(host="134.175.87.30", port=3306, user="root", passwd="", db="test",charset="utf8")
print(conn)

def CheckCommentIfExist(comment_id:str)->bool:
    """
check comment id whether existed , if yes return True,not return False
    :param comment_id: article id
    :return: if yes return True,not return False
    """
    cur = conn.cursor()
    sql = "SELECT COUNT(comment_id) AS num FROM bbs_comment WHERE comment_id = '{}'".format(comment_id)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        # Auto_KeepConnect()
        return False
    num = cur.fetchone()[0]
    cur.close()
    if num == 1:
        return True
    else:
        return False
def GetCommentOwner(comment_id:str)->str:
    """
get an comment's owner user_id.
    :param comment_id: comment id
    :return: user_id,failed or no such article_id return a void string
    """
    cur = conn.cursor()
    sql = "SELECT user_id FROM bbs_comment WHERE comment_id = '{}'".format(comment_id)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        # Auto_KeepConnect()
        return ""
    if num == 1:
        user_id = cur.fetchone()[0]
        print("user_id:",user_id)
        cur.close()
        return user_id
    else:
        cur.close()
        return ""
def UpdateComment(user_id:str,comment_id:str,content:str,id:int=-1)->dict:
    cur = conn.cursor()
    check_if_exist = CheckCommentIfExist(comment_id)
    if not check_if_exist:
        # status 100 Error article_id 评论id错误
        return {"id": id, "status": 100, "message": "Error article_id", "data": ""}
    check_user_id = GetCommentOwner(comment_id)
    if check_user_id != user_id:
        # status 101 Error user_id 用户id不匹配
        return {"id": id, "status": 101, "message": "Error user_id", "data": ""}

    update_time = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())
    sql = "UPDATE bbs_comment SET content = '{}',update_time = '{}' " \
          "WHERE comment_id = '{}' AND user_id = '{}'".format(content, update_time, comment_id, user_id)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        # Auto_KeepConnect()
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    cur.close()
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {"comment_id": comment_id}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

if __name__ == '__main__':
    user_id = "13750687010"
    comment_id = "76bd7b76fcd0b23f3d171f39b416d936"
    content = "这是一条更新过的评论"
    print(UpdateComment(user_id=user_id,comment_id=comment_id,content=content))
