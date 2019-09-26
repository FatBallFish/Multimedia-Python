from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from configparser import ConfigParser
import logging,sys
import random

# 短信应用SDK AppID
appid=""
# 短信应用SDK AppKey
appkey=""
# 定义单发信息组件
ssender = SmsSingleSender(appid, appkey)
# 定义log对象
log_sms = logging.getLogger("SmsCaptcha")
def Initialize(cfg_path,main_path):
    """
SmsCaptcha 模块初始化，此函数应在所有函数之前调用
    :param cfg_path: 配置文件地址。
    """
    global appid,appkey,ssender
    cf = ConfigParser()
    cf.read(cfg_path)
    try:
        appid = str(cf.get("SmsCaptcha","appid"))
        appkey = str(cf.get("SmsCaptcha","appkey"))
        print("[SmsCaptcha]appid:",appid)
        print("[SmsCaptcha]addkey:",appkey)
    except Exception as e:
        log_sms.error("UnkownError:",e)
        print("UnkownError:",e)
        log_sms.info("Program Ended")
        sys.exit()
    ssender = SmsSingleSender(appid, appkey)

    global Main_filepath
    Main_filepath = main_path
    log_sms.info("Module SmsCaptcha loaded")
    print("[SmsCaptcha]Module SmsCaptcha loaded")
def SendCaptchaCode(phone_number:str, captcha:str,ext:str="",command_str:str="注册账号")->dict:
    """
    向指定手机号发送指定验证码，返回证验证结果

    :return: 字典，返回证验证结果。例：{'result': 0, 'errmsg': 'OK', 'ext': '', 'sid': '8:e5CXsVN8994a8ukmfeG20190202', 'fee': 1}
    :param phone_number: 接受验证码的手机号码，文本型
    :param captcha: 将要发送的验证码内容，文本型qq
    """
    # 需要发送短信的手机号码
    # phone_numbers = ["13750687010","13958565395"]
    # 短信模板ID，需要在短信应用中申请
    template_id = 176189  # 验证码模版id
    # 签名
    # NOTE: 这里的签名"腾讯云"只是一个示例，真实的签名需要在短信控制台中申请，另外签名参数使用的是`签名内容`，而不是`签名ID`
    sms_sign = "本小宅"
    # print("checkcode:",checkcode)
    # 模版参数，具体根据短信模版中定义的参数进行
    params = [command_str, captcha, 3]
    try:
        result = ssender.send_with_param(86, phone_number, template_id, params, sign=sms_sign, extend="", ext=ext)
        # 签名参数未提供或者为空时，会使用默认签名发送短信
    except HTTPError as e:
        # print(e)
        log_sms.error("HTTPError:",e)
        return e
    except Exception as e:
        # print(e)
        log_sms.error("UnkownError:",e)
        return e
    print(result)
    try:
        if result["result"] == 0:
            log_sms.info("Successful send captcha to [%s],fee:[%s]",phone_number,result["fee"])
            print("Successful send captcha to [%s],fee:[%s]"%(phone_number,result["fee"]))
        else:
            log_sms.info("Failed to send captcha to [%s]:Error:%d,%s",phone_number,result["result"],result["errmsg"])
            print("Failed to send captcha to [%s]:Error:%d,%s"%(phone_number,result["result"],result["errmsg"]))
    except KeyError as e:
        try:
            ErrorInfo = result["ErrorInfo"]
            log_sms.error("Failed to send captcha to [%s]:ErrorInfo:%s",phone_number,ErrorInfo)
            print("Failed to send captcha to [%s]:ErrorInfo:%s"%(phone_number,ErrorInfo))
        except Exception as e:
            log_sms.error("UnkonwnError:",e)
            print("UnkonwnError:"%e)
    # log_sms.info(result)
    return result

if __name__ == "__main__":
    result = SendCaptchaCode("13750687010", "1234")
    print(result)
    # print(imgcode.code_str,imgcode.webpath)

