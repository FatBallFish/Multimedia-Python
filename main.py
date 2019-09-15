from flask import Flask,request
from m_mysql import py_mysql as MySQL
from m_img import py_captcha_main as ImgCaptcha
from m_sms import py_sms_main as SmsCaptcha
from m_redis import py_redis as Redis
from m_cos import  py_cos_main as Cos
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
    print("Progarm run at [{}]".format(time.strftime("%Y:%m:%d %H:%M:%S",time.localtime())))
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
        global log_outpath, webhost, webport, webdebug,allowurl
        log_outpath = cf.get("Main", "logoutpath")
        webhost = cf.get("Main", "webhost")
        webport = cf.get("Main", "webport")
        intdebug = cf.get("Main", "webdebug")
        allowurl = str(cf.get("COS","allowurl")).split(",")
        print("allowurl:{}".format(allowurl))
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
    Cos.Initialize(config_addr,Main_filepath)

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


@app.route("/ping")
def ping():
    return "<h1>Pong</h1>"

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
        if key not in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    # 处理json
    if data["type"] == "login":
        if data["subtype"] == "pass":
            data = data["data"]
            for key in data.keys():
                if key not in ["phone","pass","enduring"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            phone = data["phone"]
            password = data["pass"]
            # todo check salt
            if "enduring" in data.keys():
                enduring = data["enduring"]
                if not isinstance(enduring,int):
                    enduring = 0
                if enduring != 0:
                    enduring = 1
            else:
                enduring = 0
            # print(password)
            status,result = MySQL.Login(phone,password,enduring=enduring)
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
        if key not in data.keys():
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
                # status 400 hash不存在
                return json.dumps({"id": id, "status": 400, "message": "Error hash", "data": {}})

            status,result = MySQL.Register(phone,password)
            if status == 0:
                # status 0 注册成功
                return json.dumps({"id": id, "status": 0, "message": "Successful", "data": {}})
            else:
                # status -100,-200,100,101,102 Mysql处理结果
                return json.dumps({"id": id, "status": status, "message": result, "data": {}})
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/user/password",methods=["POST"])
def password():
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
        if key not in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    # 处理json
    if data["type"] == "password":
        if data["subtype"] == "forget":
            data = data["data"]
            for key in data.keys():
                if key not in ["phone", "hash", "pass"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            phone = data["phone"]
            hash = data["hash"]
            password = data["pass"]
            # todo check salt
            result = Redis.SafeCheck(hash)
            if result == False:
                # status 400 hash不存在
                return json.dumps({"id": id, "status": 400, "message": "Error hash", "data": {}})
            json_dict = MySQL.ForgetPass(phone=phone, password=password,id=id)
            return json.dumps(json_dict)
        elif data["subtype"] == 'change':
            data = data["data"]
            for key in data.keys():
                if key not in ["phone", "old", "new"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            phone = data["phone"]
            old = data["old"]
            new = data["new"]
            json_dict = MySQL.ChangePass(phone=phone,old=old,new=new,id=id)
            return json.dumps(json_dict)
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
            # status -100 Missing necessary args api地址中缺少token参数
            return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
            if key not in data.keys():
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
                    if key not in ["phone","name", "nickname","email","level"]:
                        # status -3 Error data key data数据中必需key缺失
                        return json.dumps(
                            {"id": id, "status": -3, "message": "Error data key", "data": {}})
                phone = data["phone"]
                temp_info = {}
                for key in data.keys():
                    if key == "phone":
                        continue
                    temp_info[key] = data[key]
                json_dict = MySQL.UpdataUserInfo(phone,temp_info,id=id)

                return json.dumps(json_dict)
            else:
                # status -2 json的value错误。
                return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
@app.route("/user/nickname",methods=["POST"])
def usernickename():
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
    # print(data)
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})

    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type", "subtype", "data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    type = data["type"]
    subtype = data["subtype"]
    data = data["data"]
    # 处理json
    if type == "info":
        if subtype == "nickname":
            if "user_id" not in data.keys():
                # status -3 json的value错误。
                return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            user_id = data['user_id']
            json_dict = MySQL.GetUserNicknaem(user_id=user_id,id=id)
            return json.dumps(json_dict)
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


@app.route("/portrait",methods=["POST"])
def portrait():
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
    # print(data)
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})

    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type", "subtype", "data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    type = data["type"]
    subtype = data["subtype"]
    data = data["data"]
    # 处理json
    if type == "portrait":
        if subtype == "upload":
            for key in ["base64"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            img_base64 = str(data["base64"])
            base64_head_index = img_base64.find(";base64,")
            if base64_head_index != -1:
                print("进行了替换")
                img_base64 = img_base64.partition(";base64,")[2]
            # print("-------接收到数据-------\n", img_base64, "\n-------数据结构尾-------")
            if "type" in data.keys():
                img_type = data["type"]
            img_file = base64.b64decode(img_base64)
            try:
                Cos.bytes_upload(img_file,"portrait/{}".format(username))
                print("Add portrait for id:{}".format(username))
                log_main.info("Add portrait for id:{}".format(username))
            except Exception as e:
                print("Failed to add portrait for id:{}".format(username))
                print(e)
                log_main.error("Failed to add portrait for id:{}".format(username))
                log_main.error(e)


            # with open("./{}_{}.{}".format(id,name,type),"wb") as f:
            #     f.write(img_file)
            #     print("{}_{}.{}".format(id,name,type),"写出成功！")
            # status 0 成功。
            return json.dumps({"id": id, "status": 0, "message": "Successful", "data": {
                "url": "./api/get/portrait/{}".format(username)}})
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/get/portrait/<user_id>")
def get_portrait(user_id:str):
    """
获取头像API。GET请求。
    :param user_id: 用户id
    :return: 见开发文档
    """
    try:
        realip = request.headers.get("X-Real-Ip")
        # print("real ip:{},type:{}".format(realip,type(realip)))
    except Exception as e:
        print("[get_porttrait]{}".format(e))
        log_main.error("[get_porttrait]{}".format(e))
    try:
        referer = str(request.headers.get("Referer"))
        # print("referer:{}".format(referer))
        # print("referer:{},type:{}".format(referer, type(referer)))
        for url in allowurl:
            # print("Allow Url:{}".format(url))
            #todo 服务器上有bug
            index = referer.find(url)
            if index != -1:
                break
        else:
            log_main.warning("[get_porttrait]External Domain Name : {} Reference Pictures Prohibited".format(referer))
            try:
                path = os.path.join(Main_filepath, "data/image/ban.jpg")
                with open(path, "rb") as f:
                    data = f.read()
                # data = COS.bytes_download("portrait/error")
            except Exception as e:
                print("[get_porttrait]Error:Can't load the ban img.")
                log_main.error("Error:Can't load the ban img.")
                data = b""
            return data
    except Exception as e:
        print(e)
        print("[get_porttrait]Error:Can't load the error img.")
        log_main.error("Error:Can't load the error img.")
        data = b""
        return data

    # print("The client ip is :",ip)
    # srchead = "data:;base64,"
    # import base64
    # print("[get_porttrait]user_id:", user_id)
    user_id = str(user_id)
    if user_id.isdigit():
        # print("Try to get portrait data:{}".format(id))
        try:
            data = Cos.bytes_download("portrait/{}".format(user_id))
        except Exception as e:
            msg = str(e)
            code = msg.partition("<Code>")[2].partition("</Code>")[0]
            message = msg.partition("<Message>")[2].partition("</Message>")[0]
            # todo 以后要做一个判断机制
            print("[get_portrait]{}:{}".format(code,message))
            try:
                path = os.path.join(Main_filepath,"data/image/default.jpg")
                with open(path,"rb") as f :
                    data = f.read()
                # data = COS.bytes_download("portrait/error")
            except Exception as e:
                print("[get_porttrait]Error:Can't load the default img.")
                log_main.error("Error:Can't load the default img.")
                data = b""
        return data
    else:
        # print("[get_portrait]Error user_id")
        try:
            path = os.path.join(Main_filepath, "data/image/error.jpg")
            with open(path,"rb") as f:
                data = f.read()
            # data = COS.bytes_download("portrait/error")
        except Exception as e:
            print("[get_porttrait]Error:Can't load the error img.")
            log_main.error("Error:Can't load the error img.")
            data = b""
        return data

@app.route("/user/doki",methods=["GET"])
def doki():
    token = ""
    arg_dict = request.args
    try:
        token = arg_dict.get("token")
    except Exception as e:
        print(e)

    if token == None:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
        if key not in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id":id,"status":-1,"message":"Error JSON key","data":{}})

    # 处理json
    type = data["type"]
    subtype = data["subtype"]
    data = data["data"]
    if type == "img":
        if subtype == "generate":
            # data = data["data"]
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
        elif subtype == "validate":
            # data = data["data"]
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
                # status 100 验证码hash值不匹配(包括验证码过期)。
                return json.dumps({
                    "id": id,
                    "status": 100,
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
    elif type == "sms":
        if subtype == "generate":
            # data = data["data"]
            for key in data.keys():
                # if key not in ["phone","hash"]:
                if key not in ["phone"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            # hash = data["hash"]
            # result = Redis.SafeCheck(hash)
            # if result != 0:
            #     # status 400 Error Hash hash错误。
            #     return json.dumps({"id": id, "status": 400, "message": "Error Hash", "data": {}})
            command_str = "注册账号"
            if "command_type" in data.keys():
                if isinstance(data["command_type"],str):
                    if data["command_type"].isdecimal():
                        command_type = int(data["command_type"])
                    else:
                        # status -2 json的value错误。
                        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
                elif isinstance(data["command_type"],int):
                    command_type = data["command_type"]
                else:
                    # status -2 json的value错误。
                    return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
                if command_type == 1:  # 注册账号
                    command_str = "注册账号"
                if command_type == 2:  # 忘记密码
                    command_str = "忘记密码"
            phone = str(data["phone"])
            code = random.randint(10000,99999)
            result = SmsCaptcha.SendCaptchaCode(phone,code,ext=str(id),command_str=command_str)
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
        elif subtype == "delete":
            pass
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/article",methods=["POST"])
def atricle():
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
        if key not in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    # 处理json
    type = data["type"]
    subtype = data["subtype"]
    data = data["data"]
    if type == "article":
        if subtype == "add":
            for key in ["title","content"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            title = data["title"]
            content = data["content"]
            json_dict = MySQL.AddArticle(user_id=username,title=title,content=content,id=id)
            return json.dumps(json_dict)
        elif subtype == "update":
            for key in ["article_id","content"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            article_id = data["article_id"]
            content = data["content"]
            json_dict = MySQL.UpdateArticle(user_id=username,article_id=article_id,content=content,id=id)
            return json.dumps(json_dict)
        elif subtype == "delete":
            for key in ["article_id"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            article_id = data["article_id"]
            json_dict = MySQL.DeleteArticle(user_id=username,article_id=article_id,id=id)
            return json.dumps(json_dict)
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/get/article/list",methods=["GET"])
def get_article():
    try:
        token = request.args.get("token")
    except Exception as e:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    check_token_result,user_id = MySQL.Doki2(token)
    if token == None:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    if check_token_result == False:
        # status -101 Error token token不正确
        return json.dumps({"id": -1, "status": -101, "message": "Error token", "data": {}})
    # 验证身份完成，处理数据
    arg_dict = dict(request.args)
    # num = len(arg_dict)
    # if num == 1:
    #     # status Missing necessary args api地址中缺少token参数
    #     return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})

    keywords = ""
    article_id = 0
    title = ""
    content = ""
    order = "update_time DESC"
    start = 0
    num = 50
    mode = 0
    for key in arg_dict.keys():
        if key == "token":
            continue
        elif key == "article_id":
            if isinstance(arg_dict["article_id"],int):
                article_id = arg_dict["article_id"]
            elif isinstance(arg_dict["article_id"],str):
                if str(arg_dict["article_id"]).isdigit():
                    article_id = int(arg_dict["article_id"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "title":
            if isinstance(arg_dict["title"], str):
                title = arg_dict["title"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "content":
            if isinstance(arg_dict["content"], str):
                content = arg_dict["content"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "keywords":
            if isinstance(arg_dict["keywords"], str):
                keywords = arg_dict["keywords"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "order":
            if isinstance(arg_dict["order"], str):
                order = arg_dict["order"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
            order = str(arg_dict["order"])
        elif key == "start":
            if isinstance(arg_dict["start"],int):
                start = arg_dict["start"]
            elif isinstance(arg_dict["start"],str):
                if str(arg_dict["start"]).isdigit():
                    start = int(arg_dict["start"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "num":
            if isinstance(arg_dict["num"],int):
                num = arg_dict["num"]
            elif isinstance(arg_dict["num"],str):
                if str(arg_dict["num"]).isdigit():
                    num = int(arg_dict["num"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "mode":
            if isinstance(arg_dict["mode"],int):
                mode = arg_dict["mode"]
            elif isinstance(arg_dict["mode"],str):
                if str(arg_dict["mode"]).isdigit():
                    mode = int(arg_dict["mode"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        else:
            continue
    json_dict = MySQL.GetArticleList(keywords=keywords,article_id=article_id,title=title,content=content,order=order,start=start,num=num,mode=mode)
    return json.dumps(json_dict)

@app.route("/comment",methods=["POST"])
def comment():
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
        if key not in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    # 处理json
    type = data["type"]
    subtype = data["subtype"]
    data = data["data"]
    if type == "comment":
        if subtype == "add":
            for key in ["article_id","content"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
                article_id = data["article_id"]
                content = data["content"]
                father_id = ""
                if "father_id" in data.keys():
                    father_id = data["father_id"]
                json_dict = MySQL.AddComment(user_id=username,article_id=article_id,father_id=father_id,content=content,id=id)
                return json.dumps(json_dict)
        elif subtype == "update":
            for key in ["comment_id","content"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
                comment_id = data["comment_id"]
                content = data["content"]
                json_dict = MySQL.UpdateComment(user_id=username,comment_id=comment_id,content=content,id=id)
                return json.dumps(json_dict)
        elif subtype == "delete":
            for key in ["comment_id"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            comment_id = data["comment_id"]
            json_dict = MySQL.DeleteComment(user_id=username, comment_id=comment_id, id=id)
            return json.dumps(json_dict)
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/get/comment/list",methods=["GET"])
def get_comment():
    try:
        token = request.args.get("token")
    except Exception as e:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    if token == None:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    check_token_result,user_id = MySQL.Doki2(token)
    if check_token_result == False:
        # status -101 Error token token不正确
        return json.dumps({"id": -1, "status": -101, "message": "Error token", "data": {}})
    # 验证身份完成，处理数据
    id = -1
    arg_dict = dict(request.args)
    article_id = 0
    comment_id = ""
    father_id = ""
    content = ""
    order = "update_time DESC"
    start = 0
    num = 50
    user_id = ""
    for key in arg_dict.keys():
        if key == "token":
            continue
        elif key == "article_id":
            if isinstance(arg_dict["article_id"], int):
                article_id = arg_dict["article"]
            elif isinstance(arg_dict["article_id"], str):
                if str(arg_dict["article_id"]).isdigit():
                    article_id = int(arg_dict["article_id"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "comment_id":
            if isinstance(arg_dict["comment_id"], str):
                comment_id = arg_dict["comment_id"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "father_id":
            if isinstance(arg_dict["father_id"], str):
                father_id = arg_dict["father_id"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "content":
            if isinstance(arg_dict["content"], str):
                content = arg_dict["content"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "order":
            if isinstance(arg_dict["order"], str):
                order = arg_dict["order"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
            order = str(arg_dict["order"])
        elif key == "start":
            if isinstance(arg_dict["start"], int):
                start = arg_dict["start"]
            elif isinstance(arg_dict["start"], str):
                if str(arg_dict["start"]).isdigit():
                    start = int(arg_dict["start"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "num":
            if isinstance(arg_dict["num"], int):
                num = arg_dict["num"]
            elif isinstance(arg_dict["num"], str):
                if str(arg_dict["num"]).isdigit():
                    num = int(arg_dict["num"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "user_id":
            if isinstance(arg_dict["user_id"], int):
                user_id = str(arg_dict["user_id"])
            elif isinstance(arg_dict["user_id"], str):
                user_id = arg_dict["user_id"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        else:
            continue
    json_dict = MySQL.GetCommentList(article_id=article_id, comment_id=comment_id, father_id=father_id, user_id=user_id,
                                     content=content, order=order, start=start, num=num, id=id)
    return json.dumps(json_dict)

@app.route("/active",methods=["POST"])
def active():
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
        if key not in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    # 处理json
    type = data["type"]
    subtype = data["subtype"]
    data = data["data"]
    if type == "active":
        if subtype == "add":
            for key in ["title","content"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            title = str(data["title"])
            content = str(data["content"])
            start_time = ""
            end_time = ""
            if "start_time" in data.keys():
                start_time = data["start_time"]
            if "end_time" in data.keys():
                end_time = data["end_time"]
            json_dict = MySQL.AddActive(user_id=username,title=title,content=content,start_time=start_time,end_time=end_time,id=id)
            return json.dumps(json_dict)
        elif subtype == "update":
            for key in ["active_id","title","content"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            active_id = data["active_id"]
            title = data["title"]
            content = data["content"]
            start_time = ""
            end_time = ""
            if "start_time" in data.keys():
                start_time = data["start_time"]
            if "end_time" in data.keys():
                end_time = data["end_time"]
            json_dict = MySQL.UpateActive(active_id=active_id,user_id=username,title=title,content=content,start_time=start_time,end_time=end_time,id=id)
            return json.dumps(json_dict)
        elif subtype == "delete":
            for key in ["active_id"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            active_id = data["active_id"]
            json_dict = MySQL.DeleteActive(user_id=username,active_id=active_id,id=id)
            return json.dumps(json_dict)
        elif subtype == "join":
            for key in ["active_id"]:
                active_id = data["active_id"]
            json_dict = MySQL.JoinActive(active_id=active_id,user_id=username,id=id)
            return json.dumps(json_dict)
        elif subtype == "exit":
            for key in ["active_id"]:
                active_id = data["active_id"]
            json_dict = MySQL.ExitActive(active_id=active_id,user_id=username,id=id)
            return json.dumps(json_dict)
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/get/active/list",methods=["GET"])
def get_active():
    try:
        token = request.args.get("token")
    except Exception as e:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    check_token_result,user_id = MySQL.Doki2(token)
    if token == None:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    if check_token_result == False:
        # status -101 Error token token不正确
        return json.dumps({"id": -1, "status": -101, "message": "Error token", "data": {}})
    # 验证身份完成，处理数据
    arg_dict = dict(request.args)
    # num = len(arg_dict)
    # if num == 1:
    #     # status Missing necessary args api地址中缺少token参数
    #     return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})

    keywords = ""
    active_id = 0
    user_id = ""
    title = ""
    content = ""
    order = "update_time DESC"
    start = 0
    num = 50
    for key in arg_dict.keys():
        if key == "token":
            continue
        elif key == "active_id":
            if isinstance(arg_dict["active_id"],int):
                active_id = arg_dict["active_id"]
            elif isinstance(arg_dict["active_id"],str):
                if str(arg_dict["active_id"]).isdigit():
                    active_id = int(arg_dict["active_id"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "user_id":
            if isinstance(arg_dict["user_id"],int):
                user_id = str(arg_dict["user_id"])
            elif isinstance(arg_dict["user_id"],str):
                user_id = arg_dict["user_id"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "title":
            if isinstance(arg_dict["title"], str):
                title = arg_dict["title"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "content":
            if isinstance(arg_dict["content"], str):
                content = arg_dict["content"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "keywords":
            if isinstance(arg_dict["keywords"], str):
                keywords = arg_dict["keywords"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
        elif key == "order":
            if isinstance(arg_dict["order"], str):
                order = arg_dict["order"]
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id": -1, "status": -203, "message": "Arg's value type error", "data": {}})
            order = str(arg_dict["order"])
        elif key == "start":
            if isinstance(arg_dict["start"],int):
                start = arg_dict["start"]
            elif isinstance(arg_dict["start"],str):
                if str(arg_dict["start"]).isdigit():
                    start = int(arg_dict["start"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "num":
            if isinstance(arg_dict["num"],int):
                num = arg_dict["num"]
            elif isinstance(arg_dict["num"],str):
                if str(arg_dict["num"]).isdigit():
                    num = int(arg_dict["num"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        else:
            continue
    json_dict = MySQL.GetActiveList(keywords=keywords,active_id=active_id,user_id=user_id,title=title,content=content,
                                    order=order,start=start,num=num)
    return json.dumps(json_dict)

@app.route("/get/active/member")
def get_active_member():
    active_id = 0
    order = "join_time ASC"
    start = 0
    num = 50
    try:
        token = request.args.get("token")
    except Exception as e:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    check_token_result,user_id = MySQL.Doki2(token)
    if token == None:
        # status -100 Missing necessary args api地址中缺少token参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    if check_token_result == False:
        # status -101 Error token token不正确
        return json.dumps({"id": -1, "status": -101, "message": "Error token", "data": {}})
    # 验证身份完成，处理数据
    arg_dict = dict(request.args)
    for key in arg_dict.keys():
        if key == "token":
            continue
        elif key == "active_id":
            if isinstance(arg_dict["active_id"],int):
                active_id = arg_dict["active_id"]
            elif isinstance(arg_dict["active_id"],str):
                if str(arg_dict["active_id"]).isdigit():
                    active_id = int(arg_dict["active_id"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "start":
            if isinstance(arg_dict["start"],int):
                start = arg_dict["start"]
            elif isinstance(arg_dict["start"],str):
                if str(arg_dict["start"]).isdigit():
                    start = int(arg_dict["start"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        elif key == "num":
            if isinstance(arg_dict["num"],int):
                num = arg_dict["num"]
            elif isinstance(arg_dict["num"],str):
                if str(arg_dict["num"]).isdigit():
                    num = int(arg_dict["num"])
            else:
                # status -203 Arg's value type error 键值对数据类型错误
                return json.dumps({"id":-1,"status":-203,"message":"Arg's value type error","data":{}})
        else:
            continue
    json_dict = MySQL.GetActiveMember(active_id=active_id,order=order,start=start, num=num)
    return json.dumps(json_dict)

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
