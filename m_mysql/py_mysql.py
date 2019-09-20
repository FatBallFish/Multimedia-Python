from threading import Timer
from m_mysql.py_lock import Lock
import pymysql
import sys,os
import threading
import logging
from configparser import ConfigParser
import datetime
import time
import MD5,random
import re

Lock = Lock()
log_mysql = logging.getLogger("MySql")

def Initialize(cfg_path:str,main_path:str):
    """
    初始化 Pymsql 模块
    :param cfg_path: 配置文件路径
    :param main_path: 主程序运行目录
    :return:
    """
    Lock.timeout = 3
    Lock.timeout_def = Auto_KeepConnect
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
        print("[MYSQL]Connect MYSQL database successfully!")
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
        Lock.acquire(Auto_del_token,"Auto_del_token")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        # print("【Thread-Token】Deleted {} tokens".format(num))
    except Exception as e:
        conn.rollback()
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
    sql = "SELECT password,salt FROM users WHERE phone = '{}'".format(phone)
    # print(sql)
    try:
        Lock.acquire(Login,"Login")
        num = cur.execute(sql)
        # conn.commit()
        Lock.release()
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
    Register API,return a tuple(status,result string)
    :param phone: username
    :param password: with MD5
    :return: a tuple(status,result string)
    """
    cur = conn.cursor()
    sql = "SELECT phone FROM users WHERE phone='{}'".format(phone)
    try:
        Lock.acquire(Register,"Register")
        num = cur.execute(sql)
        Lock.release()
        # print("INSERT:",num)
        # conn.commit()
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
    sql = "INSERT INTO users (phone,password,createdtime,`group`,salt) " \
          "VALUES ('{}','{}','{}','__NORMAL__','{}')".format(phone,pass_db,createdtime,salt)
    # print(sql)
    try:
        Lock.acquire(Register,"Register")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql,e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql,e))
        Auto_KeepConnect()
        # status -200 sql执行失败
        return (-200,"Failure to operate database")
    if num == 1:
        ## 创建userinfo表
        sql = "INSERT INTO usersinfo (phone,`level`) VALUES ('{}',1)".format(phone)
        # print(sql)
        try:
            Lock.acquire(Register,"Register")
            num2 = cur.execute(sql)
            # print("INSERT:",num)
            conn.commit()
            Lock.release()
        except Exception as e:
            conn.rollback()
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

def ForgetPass(phone:str,password:str,id:int=-1)->dict:
    """
忘记密码，重置密码
    :param phone: 用户账号
    :param password: 新密码
    :param id: 事件请求id
    :return: json_dict
    """
    cur = conn.cursor()
    # 生成10位salt
    salt = ""
    for i in range(10):
        # 每循环一次，随机生成一个字母或数字
        # 使用ASCII码，A-Z为65-90，a-z为97-122，0-9为48-57,使用chr把生成的ASCII码转换成字符
        char1 = random.choice([chr(random.randint(65, 90)), chr(random.randint(48, 57)), chr(random.randint(97, 122))])
        salt += char1
    pass_db = MD5.md5(password, salt)
    sql = "UPDATE users SET password = '{}',salt = '{}' WHERE phone = '{}'".format(pass_db,salt,phone)
    try:
        Lock.acquire(ForgetPass, "ForgetPass")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status Failure to operate database sql语句错误
        return {"id":id,"status":-200,"message":"Failure to operate database","data":{}}
    if num == 1:
        # status 0 执行成功s
        return {"id": id, "status": 0, "message": "successful", "data": {}}
    else:
        # status -200 sql执行失败
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def ChangePass(phone:str,old:str,new:str,id:int=-1)->dict:
    """
更改用户密码
    :param phone: 用户账号
    :param old: 老密码
    :param new: 新密码
    :param id: 事件请求id
    :return: json_dict
    """
    status,message = Login(phone,old)
    if status != 0:
        # status xxxx
        return {"id":id,"status":status,"message":message,"data":{}}
    json_dict = ForgetPass(phone=phone,password=new,id=id)
    return json_dict

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
        Lock.acquire(AddToken,"AddToken")
        cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        return ""

    # 检查并删除过期的token,不删除长效token
    sql = "DELETE FROM tokens WHERE  expiration < {} AND enduring = 0".format(int(time.time()))
    # sql = "DELETE FROM tokens WHERE phone = '{}' AND expiration < {}".format(phone,int(time.time()))
    try:
        Lock.acquire(AddToken, "AddToken")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        # print("【Thread-Token】Deleted {} tokens".format(num))
    except Exception as e:
        conn.rollback()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # return ""
    # 检查并删除多余的token
    sql = "SELECT token FROM tokens WHERE (" \
          "SELECT SUM(counting) FROM tokens WHERE phone = '{0}' AND enduring = 0)>10 " \
          "AND phone = '{0}' AND enduring = 0 ORDER BY createdtime ASC".format(phone)
    try:
        Lock.acquire(AddToken, "AddToken")
        cur.execute(sql)
        Lock.release()
        # conn.commit()
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
            Lock.acquire(AddToken, "AddToken")
            cur.execute(sql)
            conn.commit()
            Lock.release()
        except Exception as e:
            conn.rollback()
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
        Lock.acquire(RefreshToken,"RefreshToken")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
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
        Lock.acquire(Doki,"Doki")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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
        Lock.acquire(Doki2,"Doki2")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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
    Lock.release()
    try:
        DisconnectDB()
    except:
        pass
    try:
        conn = pymysql.connect(host=host, port=port, user=user,
                               passwd=password,
                               db=db, charset="utf8")
    except Exception as e:
        print("[MYSQL]Failed to connect MYSQL database")
        log_mysql.error("Failed to keep connect MYSQL database")
        sys.exit()
    else:
        print("[MYSQL]Keep Connect MYSQL database successfully")
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
        Lock.acquire(UpdataUserInfo)
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    cur.close()
    # status 0 Successful 成功！
    return {"id": id, "status": 0, "message": "Successful", "data": {}}

def DeleteUser(phone:str,id:int=-1)->dict:
    """
删除用户，同时删除usersinfo,users,tokens里相关信息
    :param phone: 用户id
    :return:
    """
    cur = conn.cursor()
    sql = "DELETE usersinfo,users FROM usersinfo,users WHERE usersinfo.phone = '{0}' AND users.phone = '{0}'".format(phone)
    try:
        Lock.acquire(DeleteUser,"DeleteUser")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Get user info failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num != 2:
        # status -200 Get user info failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

    sql = "DELETE FROM tokens WHERE phone = '{}'".format(phone)
    try:
        Lock.acquire(DeleteUser,"DeleteUser")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Get user info failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num > 0:
        # status 0 successful 成功处理事件
        return {"id":id,"status":0,"message":"successful","data":{}}
    else:
        # status -200 Get user info failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def GetUserInfo(token:str="",user_id:str="",id:int=-1)->dict:
    """
    获取用户信息，返回json字典
    :param token: 用户token
    :param user_id: 用户id，此模块仅管理员用户有效
    :return: 直接返回json字典
    """
    if user_id == "":  # 判断查询方式，传user_id仅为管理员模式有效
        result,phone = Doki2(token)
        if result == False:
            # status 1 Error Token Token错误
            return {"id": id, "status": 1, "message": "Error Token","data":{}}
    else:
        phone = user_id

    cur = conn.cursor()
    sql = "SELECT * FROM usersinfo WHERE phone = '{}'".format(phone)
    try:
        Lock.acquire(GetUserInfo,"GetUserInfo")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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

def GetUserNickname(user_id:str,id:int=-1)->dict:
    cur = conn.cursor()
    sql = "SELECT nickname FROM usersinfo WHERE phone = '{}'".format(user_id)
    try:
        Lock.acquire(GetUserNickname,"GetUserNickname")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Get user info failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 0:
        cur.close()
        # status 1 user not existed phone不存在
        return {"id": id, "status": 100, "message": "user not existed", "data": {}}
    elif num == 1:
        row = cur.fetchone()
        data = {
            "nickname": row[0],
        }
        cur.close()
        # status 0 Successful phone存在
        return {"id": id, "status": 0, "message": "Successful", "data": data}
    else:
        cur.close()
        # status 200 Unkonwn user info Error 同一phone大于2条
        return {"id": id, "status": 200, "message": "Unkonwn user info Error", "data": {}}

def GetUserNickname2(user_id:str)->str:
    """
只返回用户昵称，不返回json_dict
    :param user_id: 用户id
    :return: 返回用户昵称
    """
    cur = conn.cursor()
    sql = "SELECT nickname FROM usersinfo WHERE phone = '{}'".format(user_id)
    try:
        Lock.acquire(GetUserNickname2,"GetUserNickname2")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()  # 尝试一下当sql出错后自动重连
        # status -200 Get user info failed sql语句错误
        return ""
    if num == 0:
        cur.close()
        # status 1 user not existed phone不存在
        return ""
    elif num == 1:
        row = cur.fetchone()
        return row[0]
    else:
        cur.close()
        # status 200 Unkonwn user info Error 同一phone大于2条
        return ""

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
        Lock.acquire(AddArticle,"AddArticle")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
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
        Lock.acquire(GetArticleOwner,"GetArticleOwner")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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
check article id whether existed , if yes return True,not return False
    :param article_id: article id
    :return: if yes return True,not return False
    """
    cur = conn.cursor()
    sql = "SELECT COUNT(article_id) AS num FROM bbs_article WHERE article_id = {}".format(article_id)
    try:
        Lock.acquire(CheckArticleIfExist)
        cur.execute(sql)
        Lock.release()
        # conn.commit()
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
Update an article info,return json dict ,include id,status,message,data
    :param user_id: username,default phone number
    :param article_id: article's id,using find article which will be edited
    :param content: article's content
    :param id: request event's id ,using on event handling
    :return: json dict ,include id,status,message,data
    """
    cur = conn.cursor()
    check_if_exist = CheckArticleIfExist(article_id)
    if check_if_exist == False:
        # status 100 Error article_id 文章id错误
        return {"id": id, "status": 100, "message": "Error article_id", "data": ""}
    check_user_id = GetArticleOwner(article_id)
    if check_user_id != user_id:
        # status 101 Error user_id 用户id不匹配
        return {"id":id,"status":101,"message":"Error user_id","data":""}

    update_time = time.strftime("%Y:%m:%d %H:%M:%S",time.localtime())
    sql = "UPDATE bbs_article SET content = '{}',update_time = '{}' " \
          "WHERE article_id = {} AND user_id = '{}'".format(content,update_time,article_id,user_id)
    try:
        Lock.acquire(UpdateArticle,"UpdateArticle")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    cur.close()
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
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
        Lock.acquire(DeleteArticle,"DeleteArticle")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
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

def GetArticleList(keywords:str,article_id:int,user_id:str,title:str,content:str,order:str,start:int,num:int,mode:int,id:int=-1)->dict:
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
    :param mode: 文本返回模式，1为精简模式，0为全文模式
    :param id: 请求事件id
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
                    return {"id": -1, "status": 100, "message": "Error order", "data": {}}
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
        if user_id != "":
            condition = condition + "user_id = '{}' AND ".format(user_id)
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
        Lock.acquire(GetArticleList,"GetArticleList")
        row_num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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
    for row in rows:
        article_dict = {}
        article_dict["article_id"] = row[0]
        article_dict["user_id"] = row[1]
        article_dict["nickname"] = GetUserNickname2(row[1])
        article_dict["title"] = row[2]
        article_dict["content"] = row[3]
        article_dict["create_time"] = str(row[4])
        article_dict["update_time"] = str(row[5])
        if mode == 1:
            searchObj  = re.search("<p>(.*?)<",article_dict["content"])
            if searchObj != None:
                text = searchObj.group(1)
                text = text.replace("&nbsp;", "")
                article_dict["content"] = text
        article_list.append(article_dict)
    # status 0 successful
    return {"id": id, "status": 0, "message": "successful", "data": {"num": row_num, "list": article_list}}

def CheckCommentIfExist(comment_id:str)->bool:
    """
check comment id whether existed , if yes return True,not return False
    :param comment_id: article id
    :return: if yes return True,not return False
    """
    cur = conn.cursor()
    sql = "SELECT COUNT(comment_id) AS num FROM bbs_comment WHERE comment_id = '{}'".format(comment_id)
    try:
        Lock.acquire(CheckCommentIfExist,"CheckCommentIfExist")
        cur.execute(sql)
        Lock.release()
        # conn.commit()
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

def AddComment(user_id:str,article_id:int,father_id:str,content:str,id:int=-1)->dict:
    """
Add a comment to an article,return article_id and comment_id
    :param user_id: 用户id
    :param article_id: 文章id
    :param father_id: 父评论id
    :param content: 评论内容
    :param id: 请求事件id
    :return: 返回json_dict
    """
    cur = conn.cursor()
    if not CheckArticleIfExist(article_id):
        # status 100 Error article_id 文章id错误
        return {"id": id, "status": 100, "message": "Error article_id", "data": {}}
    comment_id = MD5.md5(content,str(time.time()))
    create_time = time.strftime("%Y:%m:%d %H:%M:%S",time.localtime())
    update_time = create_time
    if father_id != "":
        if not CheckCommentIfExist(father_id):
            # status 101 Error father_id 父评论id错误
            return {"id":id,"status":101,"message":"Error father_id","data":{}}
    sql = "INSERT INTO bbs_comment (article_id,comment_id,father_id,user_id,content,create_time,update_time) VALUES " \
          "({},'{}','{}','{}','{}','{}','{}')".format(article_id,comment_id,father_id,user_id,content,create_time,update_time)
    try:
        Lock.acquire(AddComment,"AddComment")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful",
                "data": {"article_id": article_id, "comment_id": comment_id}, "father_id": father_id}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def GetCommentOwner(comment_id:str)->str:
    """
get an comment's owner user_id.
    :param comment_id: comment id
    :return: user_id,failed or no such article_id return a void string
    """
    cur = conn.cursor()
    sql = "SELECT user_id FROM bbs_comment WHERE comment_id = '{}'".format(comment_id)
    try:
        Lock.acquire(GetCommentOwner,"GetCommentOwner")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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

def UpdateComment(user_id:str,comment_id:str,content:str,id:int=-1)->dict:
    """
Update an comment info,return json dict ,include id,status,message,data
    :param user_id: username,default phone number
    :param comment_id: comment's id,using find comment which will be edited
    :param content: comment's content
    :param id: request event's id ,using on event handling
    :return: json dict ,include id,status,message,data
    """
    cur = conn.cursor()
    check_if_exist = CheckCommentIfExist(comment_id)
    if not check_if_exist:
        # status 100 Error comment_id 评论id错误
        return {"id": id, "status": 100, "message": "Error comment_id", "data": ""}
    check_user_id = GetCommentOwner(comment_id)
    if check_user_id != user_id:
        # status 101 Error user_id 用户id不匹配
        return {"id": id, "status": 101, "message": "Error user_id", "data": ""}

    update_time = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())
    sql = "UPDATE bbs_comment SET content = '{}',update_time = '{}' " \
          "WHERE comment_id = '{}' AND user_id = '{}'".format(content, update_time, comment_id, user_id)
    try:
        Lock.acquire(UpdateComment,"UpdateComment")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    cur.close()
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def DeleteComment(user_id:str,comment_id:str,id:int=-1)->dict:
    """
Delete an comment
    :param user_id: comment owner id
    :param comment_id: comment id
    :param id: request event id
    :return: json dict,include id,status,message,data
    """
    cur = conn.cursor()
    check_if_exist = CheckCommentIfExist(comment_id)
    if check_if_exist == False:
        # status 100 article_id 文章id错误
        return {"id": id, "status": 100, "message": "Error article_id", "data": ""}
    check_user_id = GetCommentOwner(comment_id)
    if check_user_id != user_id:
        # status 101 user_id不匹配
        return {"id": id, "status": 101, "message": "Error user_id", "data": ""}
    sql = "DELETE FROM bbs_comment WHERE comment_id = '{}' AND user_id = '{}'".format(comment_id, user_id)
    try:
        Lock.acquire(DeleteComment,"DeleteComment")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
    except Exception as e:
        conn.rollback()
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

def GetCommentList(article_id:int,comment_id:str,father_id:str,user_id:str,content:str,order:str,start:int,num:int,id:int=-1)->dict:
    """
获取某一篇文章下的评论列表,article_id为必传字段，father_id则选传
所有条件将进行并集查询
    :param article_id: 文章id，精确匹配
    :param comment_id: 评论id，精确匹配，为空则表示不作为条件
    :param father_id: 父评论id，精确匹配，为空则表示不作为条件
    :param user_id: 作者id，精确匹配，为空则表示不作为条件
    :param content: 评论内容，模糊匹配，为空则表示不作为条件
    :param order: 排序规则，SQL语法
    :param start: 起始索引，默认为0
    :param num: 获取记录数，默认为50
    :param id: 请求事件处理id
    :return:
    """
    cur = conn.cursor()
    if article_id == 0:
        # status 102 Error article_id 错误的文章id
        return {"id":id,"status":102,"message":"Error article_id","data":{}}
    if order != "":
        order_list_first = order.split(",")
        for order_second in order_list_first:
            order_list_second = order_second.split()
            order_third: str
            for order_third in order_list_second:
                if order_third.lower() not in ["article_id", "user_id", "title", "content", "create_time", "update_time",
                                               "asc", "desc"]:
                    # status 100 Error Order 排序规则错误
                    return {"id": -1, "status": 100, "message": "Error order", "data": {}}
        order = " ORDER BY " + order
    if num <= 0 :
        # status 101 Error num num值错误
        return {"id":id,"status":101,"message":"Error num","data":{}}
    else:
        condition = ""
        if comment_id != "":
            condition = condition + "comment_id = '{}' AND ".format(comment_id)
        if father_id != "":
            condition = condition + "father_id = '{}' AND ".format(father_id)
        if user_id != "":
            condition = condition + "user_id = '{}' AND ".format(user_id)
        if content != "":
            condition = condition + "content LIKE '%{}%' AND ".format(content)

        if condition == "":
            sql = "SELECT * FROM bbs_comment WHERE article_id = {} AND father_id = '' {}  LIMIT {} , {}".format(article_id,order,start,num)
        else:
            condition = condition.rpartition("AND ",)[0]
            sql = "SELECT * FROM bbs_comment WHERE article_id = {} AND {} {} LIMIT {} , {}".format(article_id,condition,order,start,num)
    print(sql)
    try:
        Lock.acquire(GetCommentList,"GetCommentList")
        row_num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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
    comment_list = []
    for row in rows:
        comment_dict = {}
        comment_dict["article_id"] = row[0]
        comment_dict["comment_id"] = row[1]
        comment_dict["father_id"] = row[2]
        comment_dict["user_id"] = row[3]
        comment_dict["nickname"] = GetUserNickname2(row[3])
        comment_dict["content"] = row[4]
        comment_dict["create_time"] = str(row[5])
        comment_dict["update_time"] = str(row[6])
        comment_list.append(comment_dict)
    # status 0 successful
    return {"id": id, "status": 0, "message": "successful", "data": {"num": row_num, "list": comment_list}}

def AddActive(user_id:str,title:str,content:str,start_time:str,end_time:str,id:int=-1)->dict:
    cur = conn.cursor()
    time_list = list(str(time.time()).replace(".", ""))
    time_list.reverse()
    active_id = int("".join(time_list[:8]))
    start_time = start_time.strip()
    end_time = end_time.strip()
    if start_time != "":
        try:
            check_start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(e)
            log_mysql.error(e)
            # status 102 Error time data 开始时间或结束时间格式或数据错误
            return {"id": id, "status": 102, "message": "Error format or data for time", "data": {}}
    if end_time != "":
        try:
            check_end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(e)
            log_mysql.error(e)
            # status 102 Error time data 开始时间或结束时间格式或数据错误
            return {"id": id, "status": 102, "message": "Error format or data for time", "data": {}}

    create_time = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())
    update_time = create_time
    sql = "INSERT INTO bbs_active (active_id,user_id,title,content,start_time,end_time,create_time,update_time) " \
          "VALUES ({},'{}','{}','{}','{}','{}','{}','{}')".format(active_id,user_id,title,content,start_time,end_time,create_time,update_time)
    print(sql)
    try:
        Lock.acquire(AddActive,"AddActive")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {"active_id":active_id}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def CheckActiveIfExist(active_id:int)->bool:
    """
检查活动是否存在
    :param active_id: 活动id，8位长度
    :return: 存在返回真，不存在或查询出错返回假
    """
    cur = conn.cursor()
    sql = "SELECT COUNT(active_id) as num FROM bbs_active WHERE active_id = {}".format(active_id)
    try:
        Lock.acquire(CheckActiveIfExist,"CheckActiveIfExist")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
        cur.close()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return False
    num = cur.fetchone()[0]
    if num == 1:
        return True
    else:
        return False

def CheckActiveIfJoin(active_id:int,user_id:str)->bool:
    """
检查用户是否加入了该活动
    :param active_id: 活动id
    :param user_id: 用户id
    :return: 已加入返回真，活动不存在或未加入或查询出错返回假
    """
    cur = conn.cursor()
    if not CheckActiveIfExist(active_id):
        return False
    sql = "SELECT COUNT(active_id) as num FROM active_users WHERE active_id = {} AND user_id = '{}'".format(active_id,user_id)
    try:
        Lock.acquire(CheckActiveIfJoin,"CheckActiveIfJoin")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
        cur.close()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return False
    num = cur.fetchone()[0]
    if num == 1:
        return True
    else:
        return False

def GetActiveOwner(active_id:int)->str:
    """
get an active's owner user_id.
    :param active_id: article id
    :return: user_id,failed or no such active_id return a void string
    """
    cur = conn.cursor()
    sql = "SELECT user_id FROM bbs_active WHERE active_id = {}".format(active_id)
    try:
        Lock.acquire(GetActiveOwner,"GetActiveOwner")
        num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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

def UpateActive(active_id:int,user_id:str,title:str,content:str,start_time:str,end_time:str,id:int=-1)->dict:
    """
更新活动内容
    :param active_id: 活动id，8位长度
    :param user_id: 用户id
    :param title: 活动标题
    :param content: 活动内容
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param id: 请求事件id
    :return: json_dict
    """
    cur = conn.cursor()
    if not CheckActiveIfExist(active_id):
        # status 100 Error active_id 错误的活动id
        return {"id":id,"status":100,"message":"Error active_id","data":{}}
    if GetActiveOwner(active_id) != user_id:
        # status 101 Error user_id 错误的用户id
        return {"id": id, "status": 101, "message": "Error user_id", "data": {}}
    start_time = start_time.strip()
    end_time = end_time.strip()
    if start_time != "":
        try:
            check_start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(e)
            log_mysql.error(e)
            # status 102 Error time data 开始时间或结束时间格式或数据错误
            return {"id": id, "status": 102, "message": "Error format or data for time", "data": {}}
    if end_time != "":
        try:
            check_end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(e)
            log_mysql.error(e)
            # status 102 Error time data 开始时间或结束时间格式或数据错误
            return {"id": id, "status": 102, "message": "Error format or data for time", "data": {}}

    update_time = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())
    sql = "UPDATE bbs_active SET title = '{}',content = '{}',start_time = '{}',end_time = '{}',update_time = '{}' " \
          "WHERE active_id = {} AND user_id = '{}'".format(title, content, start_time, end_time, update_time, active_id, user_id)
    print(sql)
    try:
        Lock.acquire(UpateActive,"UpateActive")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def DeleteActive(user_id:str,active_id:int,id:int=-1)->dict:
    """
删除活动内容
    :param user_id: 用户id
    :param active_id: 活动id，8位长度
    :param id: 请求事件id
    :return: json_dict
    """
    cur = conn.cursor()
    if not CheckActiveIfExist(active_id):
        # status 101 Error active_id 错误的店铺id
        return {"id":id,"status":100,"message":"Error active_id","data":{}}
    if GetActiveOwner(active_id) != user_id:
        # status 102 Error user_id 错误的店铺id
        return {"id": id, "status": 101, "message": "Error active_id", "data": {}}
    sql = "DELETE FROM bbs_active WHERE active_id = {} AND user_id = '{}'".format(active_id,user_id)
    print(sql)
    try:
        Lock.acquire(DeleteActive,"DeleteActive")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def JoinActive(active_id:int,user_id:str,id:int=-1):
    """
加入活动。
    :param active_id: 活动id
    :param user_id: 用户id
    :param id: 请求事件id
    :return:
    """
    cur = conn.cursor()
    if not CheckActiveIfExist(active_id=active_id):
        # status 100 Error active_id
        return {"id":id,"status":100,"message":"Error active_id","data":{}}
    if CheckActiveIfJoin(active_id=active_id,user_id=user_id):
        # status 102 Already joined
        return {"id": id, "status": 102, "message": "Already joined","data":{}}
    join_time = time.strftime("%Y:%m:%d %H:%M:%S",time.localtime())
    sql = "INSERT INTO active_users (active_id,user_id,join_time) VALUES ({},'{}','{}')".format(active_id,user_id,join_time)
    try:
        Lock.acquire(JoinActive,"JoinActive")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def ExitActive(active_id:int,user_id:str,id:int=-1):
    """
退出活动
    :param active_id: 活动id
    :param user_id: 用户id
    :param id: 请求事件处理id
    :return:
    """
    cur = conn.cursor()
    if not CheckActiveIfExist(active_id=active_id):
        # status 100 Error active_id
        return {"id": id, "status": 100, "message": "Error active_id","data":{}}
    if not CheckActiveIfJoin(active_id=active_id,user_id=user_id):
        # status 101 Error user_id
        return {"id": id, "status": 101, "message": "Error user_id","data":{}}
    sql = "DELETE FROM active_users WHERE active_id = {} AND user_id = '{}'".format(active_id,user_id)
    try:
        Lock.acquire(ExitActive,"ExitActive")
        num = cur.execute(sql)
        conn.commit()
        Lock.release()
        cur.close()
    except Exception as e:
        conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Failure to operate database sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    if num == 1:
        # status 0 成功处理数据
        return {"id": id, "status": 0, "message": "Successful", "data": {}}
    else:
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}

def GetActiveList(keywords:str,active_id:int,user_id:str,title:str,content:str,order:str,start:int,num:int,mode:int=0,id:int=-1)->dict:
    """
获取活动列表。
如果keywords不为空则优先使用keywords，active_id、title、content则被忽略；keywords用于title和content的并集查询，模糊匹配；
active_id、title、content可交集查询；
    :param keywords: 搜索关键字，设置后将以此关键字模糊匹配title和content字段内容,模糊匹配
    :param active_id: 活动id，精确匹配
    :param user_id: 用户id，精确匹配
    :param title: 活动标题，模糊匹配
    :param content: 活动内容，模糊匹配
    :param order: 排序规则，使用SQL语句，为空则默认以更新时间进行排序
    :param start: 起始索引，默认为0
    :param num: 获取记录数，默认为50
    :param mode: 文本返回模式，1为全文模式，0为精简模式
    :param id: 请求事件id
    :return:
    """
    cur = conn.cursor()
    if order != "":
        order_list_first = order.split(",")
        for order_second in order_list_first:
            order_list_second = order_second.split()
            order_third: str
            for order_third in order_list_second:
                if order_third.lower() not in ["active_id", "user_id", "title", "content", "create_time",
                                               "update_time","start_time","end_time"
                                               "asc", "desc"]:
                    # status 100 Error Order 排序规则错误
                    return {"id": -1, "status": 100, "message": "Error order", "data": {}}
        order = " ORDER BY " + order
    if num <= 0:
        # status 101 Error num num值错误
        return {"id": id, "status": 101, "message": "Error num", "data": {}}

    if keywords != "":
        sql = "SELECT * FROM bbs_active WHERE title LIKE '%{0}%' OR content LIKE '%{0}%' {1} LIMIT {2} , {3}".format(
            keywords, order, start, num)
    else:
        condition = ""
        if active_id != 0:
            condition = condition + "active_id = {} AND ".format(active_id)
        if user_id != "":
            condition = condition + "user_id = '{}' AND ".format(user_id)
        if title != "":
            condition = condition + "title LIKE '%{}%' AND ".format(title)
        if content != "":
            condition = condition + "content LIKE '%{}%' AND ".format(content)

        if condition == "":
            sql = "SELECT * FROM bbs_active {0} LIMIT {1} , {2}".format(order, start, num)
        else:
            condition = condition.rpartition("AND ", )[0]
            sql = "SELECT * FROM bbs_active WHERE {} {} LIMIT {} , {}".format(condition, order, start, num)
    print(sql)
    try:
        Lock.acquire(GetActiveList,"GetActiveList")
        row_num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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
        return {"id": id, "status": 0, "message": "successful", "data": {"num": 0, "list": []}}
    active_list = []
    active_dict = {}
    for row in rows:
        active_dict["active_id"] = row[0]
        active_dict["user_id"] = row[1]
        active_dict["nickname"] = GetUserNickname2(row[1])
        active_dict["title"] = row[2]
        active_dict["content"] = row[3]
        active_dict["start_time"] = str(row[4])
        active_dict["end_time"] = str(row[5])
        active_dict["create_time"] = str(row[6])
        active_dict["update_time"] = str(row[7])
        if mode == 1:
            searchObj  = re.search("<p>(.*?)<",active_dict["content"])
            if searchObj != None:
                text = searchObj.group(1)
                text = text.replace("&nbsp;", "")
                active_dict["content"] = text
        active_list.append(active_dict)
    # status 0 successful
    return {"id": id, "status": 0, "message": "successful", "data": {"num": row_num, "list": active_list}}

def GetActiveMember(active_id:int,order:str,start:int,num:int,id:int=-1)->dict:
    """
获取活动参加人员列表
    :param active_id: 活动id
    :param order: 排序规则，使用SQL语句，为空则默认以更新时间进行排序
    :param start: 起始索引，默认为0
    :param num: 获取记录数，默认为50
    :param id: 请求事件处理id
    :return:
    """
    cur = conn.cursor()
    if active_id == 0:
        # status 102 Error active_id 错误的文章id
        return {"id":id,"status":102,"message":"Error active_id","data":{}}
    if order != "":
        order_list_first = order.split(",")
        for order_second in order_list_first:
            order_list_second = order_second.split()
            order_third: str
            for order_third in order_list_second:
                if order_third.lower() not in ["active_id", "user_id", "join_time","asc", "desc"]:
                    # status 100 Error Order 排序规则错误
                    return {"id": -1, "status": 100, "message": "Error order", "data": {}}
        order = " ORDER BY " + order
    sql = """SELECT user_id FROM active_users WHERE active_id = {} {}""".format(active_id,order)
    print(sql)
    try:
        Lock.acquire(GetActiveMember,"GetActiveMember")
        row_num = cur.execute(sql)
        Lock.release()
        # conn.commit()
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
        return {"id": id, "status": 0, "message": "successful", "data": {"num": 0, "list": []}}
    mumber_list = []
    for row in rows:
        mumber_list.append(row[0])
    # status 0 successful
    return {"id": id, "status": 0, "message": "successful", "data": {"num": row_num, "list": mumber_list}}

def AdminCheck(phone:str)->bool:
    cur = conn.cursor()
    sql = "SELECT `group` FROM users WHERE phone = '{}'".format(phone)
    try:
        Lock.acquire(AdminCheck,"AdminCheck")
        row_num = cur.execute(sql)
        Lock.release()
        # conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        return False
    if row_num == 1:
        group = cur.fetchone()[0]
        if group == "__ADMIN__":
            return True
        else:
            return False
    else:
        return False

def AdminUserList(id:int=-1)->dict:
    cur = conn.cursor()
    sql = "SELECT phone,`name`,nickname,email,`level` FROM usersinfo"
    try:
        Lock.acquire(AdminUserList, "AdminUserList")
        row_num = cur.execute(sql)
        Lock.release()
        # conn.commit()
    except Exception as e:
        # conn.rollback()
        cur.close()
        print("Failed to execute sql:{}|{}".format(sql, e))
        log_mysql.error("Failed to execute sql:{}|{}".format(sql, e))
        Auto_KeepConnect()
        # status -200 Execute sql failed sql语句错误
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    rows = cur.fetchall()
    user_list = []
    for row in rows:
        user_dict = {}
        user_dict["phone"] = row[0]
        user_dict["name"] = row[1]
        user_dict["nickname"] = row[2]
        user_dict["email"] = row[3]
        user_dict["level"] = row[4]
        user_list.append(user_dict)
    return {"id":id,"status":0,"message":"successful","data":user_list}

if __name__ == '__main__':
    Initialize()