# coding=utf-8
import requests,json
import base64
import MD5

headers = {'content-type': "application/json"}
# # 发送手机短信
# data={"id":0,"type":"sms","subtype":"generate","data":{"phone":"13750687010"}}
# response = requests.post(url="http://127.0.0.1:8888/captcha",data=json.dumps(data),headers=headers)

# code = input("验证码：")
# rand = input("随机值：")
# md5 = MD5.md5(code,rand)
# print("md5:",md5)
# # 注册
# # md5 = "fc80574292e05779bbe1d494bf7481c7"
# data={"id":0,"status":0,"type":"register","subtype":"phone","data":{"phone":"13750687010","hash":md5,"pass":"wlc570Q0"}}
# response = requests.post(url="http://127.0.0.1:8888/user/register",data=json.dumps(data),headers=headers)


# # 登录
# data={"id":0,"type":"login","subtype":"pass","data":{"phone":"13750687010","pass":"wlc570Q0","enduring":1}}
# response = requests.post(url="https://dmt.lcworkroom.cn/api/user/login",data=json.dumps(data),headers=headers)
# # response = requests.post(url="http://127.0.0.1:8888/user/login",data=json.dumps(data),headers=headers)
# # print(response.text)
# 更新信息
data={"id":0,
      "type":"info",
      "subtype":"update",
      "data":{"phone":"13750687010","name":"王凌超","nickname":"FatBallFish","email":"893721708@qq.com"}}
token = "443d5e7fe77069fda1e7dbb85b5e194b"
response = requests.post(url="https://dmt.lcworkroom.cn/api/user/info?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8888/user/info?token={}".format(token),data=json.dumps(data),headers=headers)





print(response.text)