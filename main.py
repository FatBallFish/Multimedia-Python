from flask import Flask,request
from m_mysql import py_mysql as MySQL
from m_img import py_captcha_main as ImgCaptcha
from m_sms import py_sms_main as SmsCaptcha
from m_redis import py_redis as Redis
from configparser import ConfigParser
import logging,os,time,random
import sys,getopt
import json
import base64
import MD5
import threading

app = Flask(__name__)

LOG_FORMAT = "[%(asctime)-15s] - [%(name)10s]\t- [%(levelname)s]\t- [%(funcName)-20s:%(lineno)3s]\t- [%(message)s]"
DATA_FORMAT = "%Y.%m.%d %H:%M:%S %p "
log_outpath = "./my.log"
Main_filepath = os.path.dirname(os.path.abspath(__file__))
print("Main FilePath:",Main_filepath)


def Initialize(argv:list):
    """
模块初始化，此函数应在所有命令之前调用
    :param argv: 命令行参数表
    """
    # print("Enter the function")
    global config_addr
    try:
        opts,args = getopt.getopt(argv,"hc:",["config","help"])
    except getopt.GetoptError:
        print("test.py -c <ConfigFilePath> -h <help>")
        sys.exit(2)
    for opt,arg in opts:
        # print("opt,arg",opt,arg)
        if opt in ("-h","--help"):
            print("-"*80)
            print("-h or --help      Show this passage.")
            print("-c or --config    Configuration file path")
            print("-"*80)
            sys.exit()
        elif opt in("-c","--config"):
            config_addr = str(arg)
            print("config_addr:",config_addr)
            break
        else:
            # log_main.warning("Useless argv:[%s|%s]",opt,arg)
            print("Useless argv:[%s|%s]"%(opt,arg))
    else:
        # log_main.error("missing config argv")
        print("missing config argv")
        # log_main.info("Program Ended")
        sys.exit()
    cf = ConfigParser()
    try:
        cf.read(config_addr)
    except Exception as e:
        ##log_main.error("Error config file path")
        print("Error config file path")
        ##log_main.info("Program Ended")
        sys.exit()
    sections = cf.sections()
    for section in sections:
        if section not in ["Redis","SmsCaptcha","Main","COS","MYSQL"]:
            ##log_main.error("Config file missing some necessary sections")
            print("Config file missing some necessary sections")
            ##log_main.info("Program Ended")
            sys.exit()

    # 读main配置
    # TODO CONFIG
    global log_main
    try:
        global log_outpath, webhost, webport, webdebug
        log_outpath = cf.get("Main", "logoutpath")
        webhost = cf.get("Main", "webhost")
        webport = cf.get("Main", "webport")
        intdebug = cf.get("Main", "webdebug")
        if intdebug == 1:
            webdebug = True
        else:
            webdebug = False
        print("[Main]log_outpath:",log_outpath)
        print("[Main]webhost:",webhost)
        print("[Main]webport:", webport)
        print("[Main]webdebug:", webdebug)
    except Exception as e:
        print("Error")
    logging.basicConfig(filename=log_outpath, level=logging.INFO,
                        format=LOG_FORMAT.center(30),
                        datefmt=DATA_FORMAT)
    log_main = logging.getLogger(__name__)
    # ------模块初始化------
    ImgCaptcha.Initialize(config_addr,Main_filepath)
    SmsCaptcha.Initialize(config_addr,Main_filepath)
    # COS.Initialize(config_addr,Main_filepath)
    MySQL.Initialize(config_addr,Main_filepath)
    Redis.Initialize(config_addr,Main_filepath)

class MyThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        log_main.info("Start thread {} to auto del outtime code".format(self.name))
        print ("开始线程：" + self.name)
        if self.name == "AutoRemoveExpireToken":
            # lock.acquire()
            # MySQL.Auto_del_token()
            # lock.release()
            pass
        elif self.name == "AutoKeepConnect":
            MySQL.Auto_KeepConnect()
        elif self.name == "AutoRemoveExpireHash":
            # lock.acquire()
            Redis.Auto_del_hash()
            # lock.release()


@app.route("/user/login",methods=["POST"])
def login():
    data = request.json
    print(data)

    # 判断键值对是否存在
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})
    # 先获取json里id的值，若不存在，默认值为-1
    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type", "subtype", "data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    # 处理json
    if data["type"] == "login":
        if data["subtype"] == "pass":
            data = data["data"]
            for key in data.keys():
                if key not in ["phone","pass"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            phone = data["phone"]
            password = data["pass"]
            # todo check salt
            # print(password)
            status,result = MySQL.Login(phone,password)
            if status == 0:
                # status 0 登录成功，获取用户信息
                return json.dumps({"id": id, "status": 0, "message": "Successful", "data": {"token":result}})
            else:
                # status 其他错误
                return json.dumps({"id": id, "status": status, "message": result, "data": {}})
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/user/register",methods=["POST"])
def register():
    data = request.json
    print(data)
    # 判断键值对是否存在
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})
    # 先获取json里id的值，若不存在，默认值为-1
    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type", "subtype", "data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    # 处理json
    if data["type"] == "register":
        if data["subtype"] == "phone":
            data = data["data"]
            for key in data.keys():
                if key not in ["phone","hash","pass"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            phone = data["phone"]
            hash = data["hash"]
            password = data["pass"]
            # todo check salt
            result = Redis.SafeCheck(hash)
            if result == False:
                # status -4 hash不存在
                return json.dumps({"id": id, "status": -4, "message": "Error hash", "data": {}})

            status,result = MySQL.Register(phone,password)
            if status == 0:
                # status 0 注册成功
                return json.dumps({"id": id, "status": 0, "message": "Successful", "data": {}})
            else:
                # status -100,-200,100,101 Mysql处理结果
                return json.dumps({"id": id, "status": status, "message": result, "data": {}})
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/user/info",methods=["GET","POST"])
def userinfo():
    if request.method == "GET":
        token = ""
        arg_dict = request.args
        try:
            token = arg_dict.get("token")
        except Exception as e:
            print(e)

        if token == None:
            # status -1000 Missing necessary args api地址中缺少token参数
            return json.dumps({"id": id, "status": -1000, "message": "Missing necessary args", "data": {}})
        # print("token:",token)
        json_dict = dict(MySQL.GetUserInfo(token))
        return json.dumps(json_dict)
    elif request.method == "POST":
        try:
            token = request.args["token"]
            print("token:", token)
        except Exception as e:
            print("Missing necessary args")
            log_main.error("Missing necessary agrs")
            # status -100 缺少必要的参数
            return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
        token_check_result, username = MySQL.Doki2(token)
        if token_check_result == False:
            # status -101 token不正确
            return json.dumps({"id": -1, "status": -101, "message": "Error token", "data": {}})
        # 验证身份完成，处理数据
        data = request.json
        print(data)

        # 先获取json里id的值，若不存在，默认值为-1
        try:
            keys = data.keys()
        except Exception as e:
            # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
            return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})

        if "id" in data.keys():
            id = data["id"]
        else:
            id = -1

        ## 判断指定所需字段是否存在，若不存在返回status -1 json。
        for key in ["type", "subtype", "data"]:
            if not key in data.keys():
                # status -1 json的key错误。
                return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
        type = data["type"]
        subtype = data["subtype"]
        ## -------正式处理事务-------
        data = data["data"]
        if type == "info":  ## 用户信息api
            if subtype == "update":  ## 用户信息更新api
                # 判断指定所需字段是否存在，若不存在返回status -1 json。
                for key in data.keys():
                    if not key in ["phone","name", "nickname","email","level"]:
                        # status -202 Missing necessary data key-value
                        return json.dumps(
                            {"id": id, "status": -202, "message": "Missing necessary data key-value", "data": {}})
                phone = data["phone"]
                temp_info = {}
                for key in data.keys():
                    if key == "phone":
                        continue
                    temp_info[key] = data[key]
                json_dict = MySQL.UpdataUserInfo(phone,temp_info,id=id)

                return json.dumps(json_dict)


@app.route("/user/doki",methods=["GET"])
def doki():
    token = ""
    arg_dict = request.args
    try:
        token = arg_dict.get("token")
    except Exception as e:
        print(e)

    if token == None:
        # status -1000 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -1000, "message": "Missing necessary args", "data": {}})
    # print("token:",token)
    json_dict = MySQL.Doki(token)
    return json.dumps(json_dict)

@app.route("/captcha",methods=["POST"])
def captcha():
    data = request.json
    print(data)

    # 判断键值对是否存在
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})
    # 先获取json里id的值，若不存在，默认值为-1
    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type","subtype","data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id":id,"status":-1,"message":"Error JSON key","data":{}})

    # 处理json
    if data["type"] == "img":
        if data["subtype"] == "generate":
            data = data["data"]
            # code,addr = ImgCaptcha.CreatCode()
            code, b64_data = ImgCaptcha.CreatCode()
            code = code.lower()  # 将所有的验证码转成小写
            rand_str = ""
            for i in range(5):
                char1 = random.choice(
                    [chr(random.randint(65, 90)), chr(random.randint(48, 57)), chr(random.randint(97, 122))])
                rand_str += char1
            hash = MD5.md5(code,salt=rand_str)
            result = Redis.AddImgHash(hash)
                # todo 优化验证机制
            if result == False:
                # status -404 Unkown Error
                return json.dumps({
                    "id": id,
                    "status": -404,
                    "message": "Unknown Error",
                    "data":{}
                })
            # status 0 ImgCaptcha生成成功
            # return json.dumps({
            #     "id":id,
            #     "status":0,
            #     "message":"Successful",
            #     "data":{"code":code,"addr":addr,"rand":rand_str}
            return json.dumps({
                "id": id,
                "status": 0,
                "message": "Successful",
                "data": {"imgdata": b64_data, "rand": rand_str}
                # 改动：将code字段删除
            })
        elif data["subtype"] == "validate":
            data = data["data"]
            for key in data.keys():
                if key not in ["hash"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            hash = data["hash"]
            result = Redis.SafeCheck(hash)
            if result == True:
                # status 0 校验成功。
                return json.dumps({
                    "id":id,
                    "status":0,
                    "message":"successful",
                    "data":{}
                })
            elif result == False:
                # status -1 验证码hash值不匹配(包括验证码过期)。
                return json.dumps({
                    "id": id,
                    "status": -1,
                    "message": "Error captcha hash",
                    "data": {}
                })
            else:
                # status -404 Unkown Error
                return json.dumps({
                    "id": id,
                    "status": -404,
                    "message": "Unknown Error",
                    "data": {}
                })
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status":-2, "message": "Error JSON value", "data": {}})
    elif data["type"] == "sms":
        if data["subtype"] == "generate":
            data = data["data"]
            for key in data.keys():
                # if key not in ["phone","hash"]:
                if key not in ["phone"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            # hash = data["hash"]
            # result = Redis.SafeCheck(hash)
            # if result != 0:
            #     # status -4 json的value错误。
            #     return json.dumps({"id": id, "status": -4, "message": "Error Hash", "data": {}})
            phone = str(data["phone"])
            code = random.randint(10000,99999)
            result = SmsCaptcha.SendCaptchaCode(phone,code,ext=str(id))
            status = result["result"]
            message = result["errmsg"]
            if message == "OK":
                message = "Successful"
            rand_str = ""
            if status == 0:
                for i in range(5):
                    char1 = random.choice(
                        [chr(random.randint(65, 90)), chr(random.randint(48, 57)), chr(random.randint(97, 122))])
                    rand_str += char1
                hash = MD5.md5(code, salt=rand_str)
                result = Redis.AddSmsHash(hash)
                if result == False:
                    # status -404 Unkown Error
                    return json.dumps({
                        "id": id,
                        "status": -404,
                        "message": "Unknown Error",
                        "data": {}
                    })
                # status 0 SmsCaptcha生成成功
                return json.dumps({
                    "id": id,
                    "status": status,
                    "message": message,
                    "data": {"rand": rand_str}
                })
                # 改动：将code字段删除
            else:
                # status=result["result"] 遇到错误原样返回腾讯云信息
                return json.dumps({
                    "id": id,
                    "status": status,
                    "message": message,
                    "data": {}
                })
        elif data["subtype"] == "delete":
            pass
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})



if __name__ == '__main__':
    Initialize(sys.argv[1  :])
    # thread_token = MyThread(1, "AutoRemoveExpireToken", 1)
    # thread_token.start()
    # 开启线程
    thread_keep = MyThread(1, "AutoKeepConnect", 1)
    thread_keep.start()
    thread_hash = MyThread(1, "AutoRemoveExpireHash", 1)
    thread_hash.start()
    app.run(host=webhost,port=webport,debug=webdebug)
