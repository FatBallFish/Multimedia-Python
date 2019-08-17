from threading import Timer
import pymysql
import sys,os
import threading
import logging
from configparser import ConfigParser
import datetime
import time
import MD5,random

log_mysql = logging.getLogger("MySql")
lock = threading.Lock()
def Initialize(cfg_path:str,main_path:str):
    """
    初始化 Pymsql 模块
    :param cfg_path: 配置文件路径
    :param main_path: 主程序运行目录
    :return:
    """
    cf = ConfigParser()
    cf.read(cfg_path)
    global host,port,user,password,db,conn
    try:
        host = str(cf.get("MYSQL","host"))
        port = int(cf.get("MYSQL","port"))
        user = str(cf.get("MYSQL","user"))
        password = str(cf.get("MYSQL", "pass"))
        db = str(cf.get("MYSQL", "db"))
        print("[MYSQL]host:",host)
        print("[MYSQL]port:", port)
        print("[MYSQL]user:", user)
        print("[MYSQL]pass:", password)
        print("[MYSQL]db:", db)
    except Exception as e:
        log_mysql.error("UnkownError:",e)
        print("UnkownError:",e)
        log_mysql.info("Program Ended")
        sys.exit()
    try:
        conn = pymysql.connect(host=host, port=port, user=user,
                               passwd=password,
                               db=db, charset="utf8")
    except Exception as e:
        print("Failed to connect MYSQL database")
        log_mysql.error("Failed to connect MYSQL database")
        sys.exit()
    else:
        print("Connect MYSQL database successfully!")
    global Main_filepath
    Main_filepath = main_path
    log_mysql.info("Module MySQL loaded")

def DisconnectDB():
    conn.close()

def Auto_del_token():
    """
    线程，自动删除过期token
    暂时不用，所有功能整合到Addtoken里了
    :return:
    """
    cur = conn.cursor()
    sql = "DELETE FROM tokens WHERE expiration < {}".format(int(time.time()))
    try:
        lock.acquire()
        num = cur.execute(sql)
        conn.commit()
        lock.release()
        # print("【Thread-Token】Deleted {} tokens".format(num))
    except Exception as e:
        # conn.rollback()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
    cur.close()
    ## 下面的代码似乎是用来删除超出10条的记录，我放在addtoken里删除了
    # sql = "SELECT phone,createdtime FROM tokens GROUP BY phone"
    # try:
    #     num = cur.execute(sql)
    #     conn.commit()
    # except Exception as e:
    #     # conn.rollback()
    #     cur.close()
    #     print("Failed to execute sql:{}|{}".format(sql, e))
    #     log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
    #     time.sleep(3)
    #     continue
    # data = cur.fetchall()

    # # todo 喵喵喵？？？？
    #
    # for row in data :
    #     sql = 'DELETE FROM tokens WHERE ' \
    #           '((SELECT COUNT(phone) as num FROM tokens WHERE phone ="{0}") > 10 AND phone IN ' \
    #           '(SELECT phone FROM tokens WHERE phone = "{0}" ORDER BY createdtime ASC LIMIT num-10))'.format(row[0])
    #     try:
    #         num = cur.execute(sql)
    #         conn.commit()
    #         print("【Thread-Token】10:Deleted {} tokens".format(num))
    #     except Exception as e:
    #         conn.rollback()
    #         print("Thread-Token:Failed to execute sql:{}".format(sql))
    #         print(e)
    #         log_mysql.error("Failed to execute sql:{}".format(sql))

def Login(phone:str,password:str,enduring:int=0)->tuple:
    """
    Login API,return a tuple(status,result string)
    :param phone: username
    :param password: with base64
    :return: a tuple(status,result string)
    """
    cur = conn.cursor()
    sql = 'SELECT password,salt FROM users WHERE phone = "{}"'.format(phone)
    # print(sql)
    try:
        num = cur.execute(sql)
        # print("num:",num)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql,e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql,e))
        Auto_KeepConnect()
        # status -200 sql执行失败
        return (-200,"Failure to operate database")

    if num == 1:
        row = cur.fetchone()
        pass_db = row[0]
        salt = row[1]
        cur.close()
        if pass_db == MD5.md5(password,salt):
            token = AddToken(phone,enduring=enduring)
            if token == "":
                # status 300 添加token失败
                return (300,"Add token failed")
            # status 0 执行成功，返回token
            return (0,token)
        else:
            # status 101 账号密码错误
            return (101,"Error password")
    elif num == 0:
        # status 100 无记录
        return (100,"Incorrect user")
    else:
        # status 200 记录数量有误
        return (200,"Invalid record number")

def Register(phone:str,password:str)->tuple:
    """
    Login API,return a tuple(status,result string)
    :param phone: username
    :param password: with base64
    :return: a tuple(status,result string)
    """
    cur = conn.cursor()
    sql = "SELECT phone FROM users WHERE phone='{}'".format(phone)
    try:
        num = cur.execute(sql)
        # print("INSERT:",num)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql,e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql,e))
        Auto_KeepConnect()
        # status -200 sql执行失败
        return (-200,"Failure to operate database")
    if num > 0:
        # status 101 手机号已存在
        return (101,"Phone number existed")
    createdtime = time.strftime("%Y:%m:%d %H:%M:%S",time.localtime())

    # 生成10位salt
    salt = ""
    for i in range(10):
        # 每循环一次，随机生成一个字母或数字
        # 使用ASCII码，A-Z为65-90，a-z为97-122，0-9为48-57,使用chr把生成的ASCII码转换成字符
        char1 = random.choice([chr(random.randint(65,90)),chr(random.randint(48,57)),chr(random.randint(97,122))])
        salt += char1
    pass_db = MD5.md5(password,salt)
    sql = 'INSERT INTO users (phone,password,createdtime,`group`,salt) ' \
          'VALUES ("{}","{}","{}","__NORMAL__","{}")'.format(phone,pass_db,createdtime,salt)
    # print(sql)
    try:
        num = cur.execute(sql)
        # print("INSERT:",num)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql,e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql,e))
        Auto_KeepConnect()
        # status -200 sql执行失败
        return (-200,"Failure to operate database")
    if num == 1:
        ## 创建userinfo表
        sql = 'INSERT INTO usersinfo (phone,`level`) VALUES ("{}",1)'.format(phone)
        # print(sql)
        try:
            num2 = cur.execute(sql)
            # print("INSERT:",num)
            conn.commit()
        except Exception as e:
            # conn.rollback()
            cur.close()
            print("Failed to execute sql:{}|{}".format(sql, e))
            log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
            Auto_KeepConnect()
            # status -200 sql执行失败
            return (-200, "Failure to operate database")
        cur.close()
        if num2 == 1:
            # status 0 执行成功，返回token
            return (0, "Successful")
        elif num2 == 0:
            # status 102 创建用户信息失败
            return (102, "Incorrect user information")
        else:
            # status 200 记录数量有误
            return (200, "Invalid record number")
    elif num == 0:
        cur.close()
        # status 100 无记录
        return (101,"Incorrect user data")
    else:
        cur.close()
        # status 200 记录数量有误
        return (200,"Invalid record number ")

def AddToken(phone:str,enduring:int=0)->str:
    """
    Add token in database
    :param phone: username
    :return: result string,success return token,failed return void string.
    """
    createdtime = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())
    time_now = int(time.time())
    time_expiration = time_now + 10 * 60
    token = MD5.md5(phone+str(time_now),"dmt")
    cur = conn.cursor()
    sql = 'INSERT INTO tokens (token,phone,createdtime,expiration,counting,enduring)' \
          'VALUES ("{}","{}","{}",{},{},{})'.format(token,phone,createdtime,time_expiration,1,enduring)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        return ""

    # 检查并删除过期的token,不删除长效token
    sql = "DELETE FROM tokens WHERE  expiration < {} AND enduring = 0".format(int(time.time()))
    # sql = "DELETE FROM tokens WHERE phone = '{}' AND expiration < {}".format(phone,int(time.time()))
    try:
        num = cur.execute(sql)
        conn.commit()
        # print("【Thread-Token】Deleted {} tokens".format(num))
    except Exception as e:
        # conn.rollback()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # return ""
    # 检查并删除多余的token
    sql = "SELECT token FROM tokens WHERE (" \
          "SELECT SUM(counting) FROM tokens WHERE phone = '{0}' AND enduring = 0)>10 " \
          "AND phone = '{0}' AND enduring = 0 ORDER BY createdtime ASC".format(phone)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        return ""
    data = cur.fetchall()
    num = len(data)
    # print("over num:",num)
    data = data[0:(num-10)]
    for row in data:
        sql = "DELETE FROM tokens WHERE token = '{}'".format(row[0])
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            # conn.rollback()
            cur.close()
            print("Failed to execute sql:{}|{}".format(sql, e))
            log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
            Auto_KeepConnect()
            return ""
        print("Deleted over-flowing record:{}".format(row[0]))

    cur.close()
    # 全部成功返回新token
    return token

def RefreshToken(token:str)->bool:
    """
    刷新token过期时间
    :param token:token值
    :return:返回处理结果，成功为True，否则False
    """
    cur = conn.cursor()
    sql = "UPDATE tokens SET expiration = {} WHERE token = '{}'".format(int(time.time()+600),token)
    try:
        num = cur.execute(sql)
        conn.commit()
        cur.close()
    except Exception as e:
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        return False
    return True

def Doki(token:str,id:int=-1)->dict:
    """
    检测token是否有效，返回json字典，若有效自动刷新token过期时间
    :param token: token值
    :return: 直接返回json字典
    """
    cur = conn.cursor()
    sql = "SELECT token FROM tokens WHERE token = '{}'".format(token)
    try:
        num = cur.execute(sql)
        conn.commit()
        cur.close()
    except Exception as e:
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Get Doki info failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 0:
        # status 1 Token not existed Token不存在
        return {"id": id, "status": 1, "message": "Token not existed", "data": {}}
    elif num == 1:
        RefreshToken(token)
        # status 0 Successful Token存在
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
    else:
        # status 200 Unkonwn token Error 同一Token大于2条
        return {"id": id, "status": 200, "message": "Invalid token number", "data": {}}

def Doki2(token:str)->tuple:
    """
    检测token是否有效，返回一个由bool值和用户名的组成的元组，若有效自动刷新token过期时间
    :param token: token值
    :return: 返回逻辑值，真为token存在，假为token不存在
    """
    cur = conn.cursor()
    sql = "SELECT phone FROM tokens WHERE token = '{}'".format(token)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Failure to operate database语句错误
        return (False,"")

    if num == 1:
        data = cur.fetchone()
        cur.close()
        phone = data[0]
        RefreshToken(token)
        # status 0 Successfully Token存在
        return (True,phone)
    else:
        cur.close()
        # status -404 Unkonwn token Error 同一Token大于2条
        return (False,"")

def Auto_KeepConnect():
    """
    每十分钟定时断开数据库并重连，保持连接活性
    :return:
    """
    global conn
    DisconnectDB()
    try:
        conn = pymysql.connect(host=host, port=port, user=user,
                               passwd=password,
                               db=db, charset="utf8")
    except Exception as e:
        print("Failed to connect MYSQL database")
        log_mysql.error("Failed to keep connect MYSQL database")
        sys.exit()
    else:
        print("Keep Connect MYSQL database successfully")
        log_mysql.info("Keep Connect MYSQL database successfully")
    timer = Timer(600, Auto_KeepConnect)
    timer.start()

def UpdataUserInfo(phone:str,info:dict,id:int=-1)->dict:
    """
Update user info ,return json dict,include id,status,message,data
    :param phone:
    :param info:
    :param id:
    :return: return json dict
    """
    cur = conn.cursor()
    sql = "UPDATE usersinfo SET "
    for key in info.keys():
        sql = sql + key + " = '{}' ,".format(info[key])
    sql = sql.rpartition(",")[0]
    sql = sql + "WHERE phone = '{}'".format(phone)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    cur.close()
    # status 0 Successful 成功！
    return {"id": id, "status": 0, "message": "Successful", "data": {}}

def GetUserInfo(token:str,id:int=-1)->dict:
    """
    获取用户信息，返回json字典
    :param token:
    :return: 直接返回json字典
    """
    result,phone = Doki2(token)
    if result == False:
        # status 1 Error Token Token错误
        return {"id": id, "status": 1, "message": "Error Token","data":{}}
    cur = conn.cursor()
    sql = "SELECT * FROM usersinfo WHERE phone = '{}'".format(phone)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Get user info failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data":{}}
    if num == 0:
        cur.close()
        # status 1 user not existed phone不存在
        return {"id": id, "status": 1, "message": "user not existed", "data": {}}
    elif num == 1:
        RefreshToken(token)
        row = cur.fetchone()
        data = {
            "phone":row[0],
            "name":row[1],
            "nickname":row[2],
            "email":row[3],
            "level":row[4],
        }
        cur.close()
        # status 0 Successful phone存在
        return {"id": id, "status": 0, "message": "Successful", "data":data}
    else:
        cur.close()
        # status 200 Unkonwn user info Error 同一phone大于2条
        return {"id": id, "status": 200, "message": "Unkonwn user info Error", "data": {}}
    # todo invavild

def AddArticle(user_id:str,title:str,content:str,id:int=-1)->dict:
    """
Add an article to bbs,return json dict ,include id,status,message,data
    :param user_id: username,default phone number
    :param title: article's title ,display at the top
    :param content: article's content
    :param id: request event's id ,using on event handling
    :return: json dict ,include id,status,message,data
    """
    cur = conn.cursor()
    article_id = int(time.time())
    create_time = time.strftime("%Y:%m:%d %H:%M:%S",time.localtime())
    update_time = create_time
    sql = "INSERT INTO bbs_article (article_id,user_id,title,content,create_time,update_time) " \
          "VALUES ({},'{}','{}','{}','{}','{}')".format(article_id,user_id,title,content,create_time,update_time)
    try:
        num = cur.execute(sql)
        conn.commit()
        cur.close()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {"article_id":article_id}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def GetArticleOwner(article_id:int)->str:
    """
get an article's owner user_id.
    :param article_id: article id
    :return: user_id,failed or no such article_id return a void string
    """
    cur = conn.cursor()
    sql = "SELECT user_id FROM bbs_article WHERE article_id = {}".format(article_id)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        return ""
    if num == 1:
        user_id = cur.fetchone()[0]
        print("user_id:",user_id)
        cur.close()
        return user_id
    else:
        cur.close()
        return ""

def CheckArticleIfExist(article_id:int)->bool:
    """
check article id whether existed , if yes retuen True,not return False
    :param article_id: article id
    :return: if yes retuen True,not return False
    """
    cur = conn.cursor()
    sql = "SELECT SUM(article_id) AS num FROM bbs_article WHERE article_id = {}".format(article_id)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        return False
    num = cur.fetchone()[0]
    cur.close()
    if num == 1:
        return True
    else:
        return False

def UpdateArticle(user_id:str,article_id:int,content:str,id:int=-1)->dict:
    """
Add an article to bbs,return json dict ,include id,status,message,data
    :param user_id: username,default phone number
    :param article_id: article's id,using find article which will be edited
    :param content: article's content
    :param id: request event's id ,using on event handling
    :return: json dict ,include id,status,message,data
    """
    cur = conn.cursor()
    check_if_exist = CheckArticleIfExist(article_id)
    if check_if_exist == False:
        # status 100 article_id 文章id错误
        return {"id": id, "status": 100, "message": "Error article_id", "data": ""}
    check_user_id = GetArticleOwner(article_id)
    if check_user_id != user_id:
        # status 101 Error user_id 用户id不匹配
        return {"id":id,"status":101,"message":"Error user_id","data":""}

    update_time = time.strftime("%Y:%m:%d %H:%M:%S",time.localtime())
    sql = "UPDATE bbs_article SET content = '{}',update_time = '{}' " \
          "WHERE article_id = {} AND user_id = '{}'".format(content,update_time,article_id,user_id)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    cur.close()
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {"article_id":article_id}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def DeleteArticle(user_id:str,article_id:int,id:int=-1)->dict:
    """
Delete an article
    :param user_id: article owner id
    :param article_id: article id
    :param id: request event id
    :return: json dict,include id,status,message,data
    """
    cur = conn.cursor()
    check_if_exist = CheckArticleIfExist(article_id)
    if check_if_exist == False:
        # status 100 article_id 文章id错误
        return {"id": id, "status": 100, "message": "Error article_id", "data": ""}
    check_user_id = GetArticleOwner(article_id)
    if check_user_id != user_id:
        # status 101 user_id不匹配
        return {"id": id, "status": 101, "message": "Error user_id", "data": ""}
    sql = "DELETE FROM bbs_article WHERE article_id = {} AND user_id = '{}'".format(article_id,user_id)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    cur.close()
    if num == 1:
        # status 0 成功处理
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def GetArticleList(keywords:str,article_id:int,title:str,content:str,order:str,start:int,num:int,id:int=-1)->dict:
    """
获取文章列表，
如果keywords不为空则优先使用keywords，article_id、title、content则被忽略；keywords用于title和content的并集查询，模糊匹配；
article_id、title、content可交集查询；
    :param keywords: 搜索关键字，设置后将以此关键字模糊匹配title和content字段内容,模糊匹配
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
            order_list_second = order_second.split()
            order_third: str
            for order_third in order_list_second:
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
            sql = "SELECT * FROM bbs_article {0} LIMIT {1} , {2}".format(order,start,num)
        else:
            condition = condition.rpartition("AND ",)[0]
            sql = "SELECT * FROM bbs_article WHERE {} {} LIMIT {} , {}".format(condition,order,start,num)
    print(sql)
    try:
        row_num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
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
    Initialize()