from flask import Flask,request
from configparser import ConfigParser
import sys,getopt
import json
import os,logging
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
        print("-" * 80)
        print("-h or --help      Show this passage.")
        print("-c or --config    Configuration file path")
        print("-" * 80)
        sys.exit()
        # log_main.info("Program Ended")
    cf = ConfigParser()
    try:
        cf.read(config_addr)
    except Exception as e:
        ##log_main.error("Error config file path")
        print("Error config file path")
        ##log_main.info("Program Ended")
        sys.exit()
    sections = cf.sections()
    if "Main" not in sections:
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
    print("Webhook-python Loaded")
    log_main.info("Webhook-python Loaded")
@app.route("/",methods=["POST"])
def python_webhook():
    data = request.json
    # print(data)
    # 判断键值对是否存在
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        log_main.error("Error request content:{}".format(data))
        return "Hello Webhook"
    # 先获取json里id的值，若不存在，默认值为-1
    print("New push request was arrived")
    log_main.info("New push request was arrived")
    if "hook_id" in data.keys():
        hook_id = data["hook_id"]
        print("[hook_id]:{}".format(hook_id))
        log_main.info("[hook_id]:{}".format(hook_id))
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["compare", "commits", "repository","sender"]:
        if not key in data.keys():
            # status -1 json的key错误。
            print("Error Json key")
            return "Hello Webhook"
    repository_dict = data["repository"]
    repository_name = repository_dict["full_name"]
    print("[repository]:{}".format(repository_name))
    log_main.info("[repository]:{}".format(repository_name))
    html_url = repository_dict["html_url"]
    print("[html_url]:{}".format(html_url))
    log_main.info("[html_url]:{}".format(html_url))

    commits_dict = data["commits"][0]
    message = commits_dict["message"]
    print("[message]:{}".format(message))
    log_main.info("[message]:{}".format(message))
    timestamp = commits_dict["timestamp"]
    print("[timestamp]:{}".format(timestamp))
    log_main.info("[timestamp]:{}".format(timestamp))

    pusher_dict = data["pusher"]
    pusher = pusher_dict["name"]
    print("[pusher]:{}".format(pusher))
    log_main.info("[pusher]:{}".format(pusher))

    compare = data["compare"]
    print("[compare]:{}".format(compare))
    log_main.info("[compare]:{}".format(compare))

    thread = threading.Thread(target=git_pull)
    thread.start()

    return "Hello Webhook"

def git_pull():


    # secret_code = hook_dict["config"]["secret"]
    # print("[secret]:{}".format(secret_code))
    # log_main.info("[secret]:{}".format(secret_code))
    # if secret_code == "IzY7HufbzRvLlHI9VdwKncIUFOnW8XRL":
    #     print("Secret code is available")
    # else:
    #     print("Error Secret code")
    #     log_main.error("Error Secret code")
    #     return "Hello Webhook"

    print("Start git pull")
    log_main.info("Start git pull")
    git = os.system("git pull origin master")
    print("Git status:{}".format(git))
    log_main.info("Git status:{}".format(git))
    print("Finish git pull")
    log_main.info("Finish git pull")
    print("Reload backend program")
    log_main.info("Reload backend program")
    status = os.system("start.bat")
    print("Finish")

if __name__ == '__main__':
    Initialize(sys.argv[1:])
    app.run(host=webhost,port=webport,debug=webdebug)