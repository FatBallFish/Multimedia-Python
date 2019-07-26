from configparser import ConfigParser
from threading import Timer
import redis
import sys,os
import logging
import time

log_redis = logging.getLogger("Redis")
imgcaptcha_list = []  #{"hash":hash,"TTL":180}
smscaptcha_list = []  #{"hash":hash,"TTL":180}

def Initialize(cfg_path:str,main_path:str):
    """
    初始化Postgresql模块
    :param cfg_path: 配置文件路径
    :param main_path: 主程序运行目录
    :return:
    """
    cf = ConfigParser()
    cf.read(cfg_path)
    global host,port,user,password,db,conn,r
    # 读Redis配置
    try:
        r_host = cf.get("Redis", "host")
        r_port = cf.get("Redis", "port")
        r_db = cf.get("Redis", "db")
        r_pass = cf.get("Redis", "pass")
        global r_imgsetname, r_smssetname
        r_imgsetname = cf.get("Redis", "img_setname")  # TODO global setname
        r_smssetname = cf.get("Redis", "sms_setname")
        print("[Redis]Host:", r_host)
        print("[Redis]Port:", r_port)
        print("[Redis]DB:", r_db)
        print("[Redis]Imgsetname:", r_imgsetname)
        print("[Redis]Smssetname:", r_smssetname)
    except Exception as e:
        log_redis.error(e)
        print(e)
        log_redis.info("Program Ended")
        sys.exit()

    # 启动Redis 并初始化验证码库
    try:
        r = redis.StrictRedis(host=r_host, port=r_port, db=r_db, password=r_pass)
        r.set("check","1")
        r.delete("check")
    except Exception as e:
        log_redis.error(e)
        print(e)
        log_redis.info("Program Ended")
        sys.exit()
    else:
        print("Connect Redis database successfully!")
    try:
        r.delete(r_imgsetname)
        print("Delete Redis's set [%s]" % r_imgsetname)
    except Exception as e:
        pass
    try:
        r.delete(r_smssetname)
        print("Delete Redis's set [%s]" % r_smssetname)
    except Exception as e:
        pass

    global Main_filepath
    Main_filepath = main_path
    log_redis.info("Module Redis loaded")

def Auto_del_hash():
    for imgcaptcha in imgcaptcha_list:
        if r.sismember(r_imgsetname, imgcaptcha["hash"]) == False:
            print("imghash:[%s]had deleted" % imgcaptcha["hash"])
            imgcaptcha_list.remove(imgcaptcha)
            continue
        # print("imghash:", imgcaptcha["hash"], "sis:", )
        if imgcaptcha["TTL"] <= 0:
            try:
                print("Try to remove hash [%s]" % imgcaptcha["hash"])
                r.srem(r_imgsetname,imgcaptcha["hash"])
            except Exception as e:
                log_redis.error(e)
                print(e)
            index = imgcaptcha_list.index(imgcaptcha)
            imgcaptcha_list.pop(index)
            continue
        imgcaptcha["TTL"] -= 3
        # print(imgcaptcha["hash"],imgcaptcha["TTL"])
    for smscaptcha in smscaptcha_list:
        if r.sismember(r_smssetname, smscaptcha["hash"]) == False:
            print("smshash:[%s]had deleted" % smscaptcha["hash"])
            smscaptcha_list.remove(smscaptcha)
            continue
        if smscaptcha["TTL"] <= 0:
            try:
                print("Try to remove hash [%s]" % smscaptcha["hash"])
                r.srem(r_smssetname,smscaptcha["hash"])
            except Exception as e:
                log_redis.error(e)
                print(e)
            index = smscaptcha_list.index(smscaptcha)
            smscaptcha_list.pop(index)
            continue
        smscaptcha["TTL"] -= 3
        # print(smscaptcha["hash"], smscaptcha["TTL"])
    timer = Timer(3, Auto_del_hash)
    timer.start()

def AddImgHash(hash:str)->bool:
    """
    Add ImgCaptcha hash to redis,return result
    :param hash: Md5(code+rand)
    :return: Whether success to add record.True or False
    """
    try:
        r.sadd(r_imgsetname, hash)
        imgcaptcha_list.append({"hash": hash, "TTL": 180})
    except Exception as e:
        log_redis.error(e)
        print(e)
        return False
    return True

def AddSmsHash(hash:str):
    try:
        r.sadd(r_smssetname, hash)
        smscaptcha_list.append({"hash": hash, "TTL": 180})
        # todo 优化验证机制
    except Exception as e:
        log_redis.error(e)
        print(e)
        return False
    return True

def SafeCheck(hash)->bool:
    """
    Check imgcaptcha or smscaptcha hash
    :param hash:
    :return: exist return True,non-exist return False
    """
    flag = False
    for imgcaptcha in imgcaptcha_list :
        if imgcaptcha["hash"] == hash:
            flag = True
            imgcaptcha["TTL"] = 180
            break
        else:
            pass
    for smscaptcha in smscaptcha_list :
        if smscaptcha["hash"] == hash:
            flag = True
            smscaptcha["TTL"] = 180
            break
        else:
            pass
    if flag == True:
        return True
    else:
        return False