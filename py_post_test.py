# coding=utf-8
import requests,json
import base64
import MD5

headers = {'content-type': "application/json"}
# # 发送手机短信
# data={"id":0,"type":"sms","subtype":"generate","data":{"phone":"15857174214"}}
# response = requests.post(url="http://127.0.0.1:8765/captcha",data=json.dumps(data),headers=headers)
#
# code = input("验证码：")
# rand = input("随机值：")
# md5 = MD5.md5(code,rand)
# print("md5:",md5)
# # 注册
# # md5 = "fc80574292e05779bbe1d494bf7481c7"
# data={"id":0,"status":0,"type":"register","subtype":"phone","data":{"phone":"13750687010","hash":md5,"pass":"wlc570Q0"}}
# response = requests.post(url="http://127.0.0.1:8888/user/register",data=json.dumps(data),headers=headers)


# 登录
# data={"id":0,"type":"login","subtype":"pass","data":{"phone":"13750687010","pass":"wlc570Q0","enduring":0}}
# response = requests.post(url="https://dmt.lcworkroom.cn/api/user/login",data=json.dumps(data),headers=headers)
# # response = requests.post(url="http://127.0.0.1:8888/user/login",data=json.dumps(data),headers=headers)
# print(response.text)

# # 更新信息
# data={"id":0,
#       "type":"info",
#       "subtype":"update",
#       "data":{"phone":"13750687010","name":"王凌超","nickname":"FatBallFish","email":"893721708@qq.com"}}
# token = "aacb6ea4eddfec38a6537b3d6d4f4b85"
# response = requests.post(url="https://dmt.lcworkroom.cn/api/user/info?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="http://127.0.0.1:8888/user/info?token={}".format(token),data=json.dumps(data),headers=headers)

# # 获取nickname
# data={"id":0,
#       "type":"info",
#       "subtype":"nickname",
#       "data":{"user_id":"13750687010"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/user/nickname?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/user/nickname?token={}".format(token),data=json.dumps(data),headers=headers)

# # 获取指定文章
# data={"article_id":1565926081}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/get/article/list?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/get/article/list?token={}".format(token),data=json.dumps(data),headers=headers)

# # 增加文章
# data={"id":0,
#       "type":"article",
#       "subtype":"add",
#       "data":{"title":"测试文章","content":"这是一篇测试文章"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# response = requests.post(url="https://dmt.lcworkroom.cn/api/article?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="http://127.0.0.1:8765/article?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新文章
# data={"id":0,
#       "type":"article",
#       "subtype":"update",
#       "data":{"article_id":1565920055,"content":"这是一篇测试文章,测试一下更新效果"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/article?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/article?token={}".format(token),data=json.dumps(data),headers=headers)

# # 删除文章
# data={"id":0,
#       "type":"article",
#       "subtype":"delete",
#       "data":{"article_id":1565920055}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/article?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/article?token={}".format(token),data=json.dumps(data),headers=headers)

# # 增加评论
# data={"id":0,
#       "type":"comment",
#       "subtype":"add",
#       "data":{"article_id":1565926081,"content":"这是一条用API请求的子级评论","father_id":"76bd7b76fcd0b23f3d171f39b416d936"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/comment?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新评论
# data={"id":0,
#       "type":"comment",
#       "subtype":"update",
#       "data":{"comment_id":"d757d9ea4c9c1860299a0341524a6a7d","content":"这是一条用API更新的子级评论2"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# response = requests.post(url="https://dmt.lcworkroom.cn/api/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/comment?token={}".format(token),data=json.dumps(data),headers=headers)

# # 删除文章
# data={"id":0,
#       "type":"comment",
#       "subtype":"delete",
#       "data":{"comment_id":"a301c03e1248eabf83785b5548d603ec"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/comment?token={}".format(token),data=json.dumps(data),headers=headers)

# # 上传头像
# with open("./temp/temp.jpg","rb") as f:
#       file_data = f.read()
# # print(file_data)
# img_base64 = str(base64.b64encode(file_data),"utf-8")
# print("base64:\n{}".format(img_base64))
# data={"id":0,
#       "type":"portrait",
#       "subtype":"upload",
#       "data":{"base64":"{}".format(img_base64)}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/portrait?token={}".format(token),data=json.dumps(data),headers=headers)

# # 增加活动
# data={"id":0,
#       "type":"active",
#       "subtype":"add",
#       "data":{"title":"校友召集令","content":"恰逢更名时机，召集校友来此一聚","start_time":"2019-08-24 00:00:00","end_time":"2019-8-25 0:0:0"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新活动
# data={"id":0,
#       "type":"active",
#       "subtype":"update",
#       "data":{"active_id":78554587,"title":"校友召集令2","content":"恰逢更名时机，召集校友来此一聚，更新活动内容","start_time":"2019-08-25 00:00:00","end_time":"2019-8-26 0:0:0"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# response = requests.post(url="https://dmt.lcworkroom.cn/api/active?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="http://127.0.0.1:8765/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 删除活动
# data={"id":0,
#       "type":"active",
#       "subtype":"delete",
#       "data":{"active_id":86889745}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 加入活动
# data={"id":0,
#       "type":"active",
#       "subtype":"join",
#       "data":{"active_id":78554587}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 退出活动
# data={"id":0,
#       "type":"active",
#       "subtype":"exit",
#       "data":{"active_id":78554587}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/active?token={}".format(token),data=json.dumps(data),headers=headers)

# 修改密码
# data={"id":0,
#       "type":"password",
#       "subtype":"change",
#       "data":{"phone":"13750687010",
#               "old":"abc123",
#               "new":"wlc570Q0"}}
# # token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/user/password",data=json.dumps(data),headers=headers)

# # 获取用户列表（管理员）
# data={"id":0,
#       "type":"user",
#       "subtype":"list",
#       "data":{}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/user?token={}".format(token),data=json.dumps(data),headers=headers)

# # 获取用户信息（管理员）
# data={"id":0,
#       "type":"user",
#       "subtype":"info",
#       "data":{"phone":"13566284913"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/user?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/user?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新用户信息（管理员）
# data={"id":0,
#       "type":"user",
#       "subtype":"update",
#       "data":{"phone":"13750687010","nickname":"FatBallFish","email":"893721708@qq.com"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/user?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/user?token={}".format(token),data=json.dumps(data),headers=headers)

# # 删除用户（管理员）
# data={"id":0,
#       "type":"user",
#       "subtype":"delete",
#       "data":{"phone":"19857160634"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/user?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/user?token={}".format(token),data=json.dumps(data),headers=headers)

# # 获取文章列表（管理员）
# # data={"id":0,
# #       "type":"article",
# #       "subtype":"list",
# #       "data":{"user_id":"13750687010"}}
# # token = "99c9150238fa21051f558ceccad55b8a"
# # # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="http://127.0.0.1:8765/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)

# # 增加文章（管理员）
# # data={"id":0,
# #       "type":"article",
# #       "subtype":"add",
# #       "data":{"user_id":"13566284913","content":"管理员增加内容","title":"管理员增加标题"}}
# # token = "99c9150238fa21051f558ceccad55b8a"
# # # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="http://127.0.0.1:8765/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新文章信息（管理员）
# data={"id":0,
#       "type":"article",
#       "subtype":"update",
#       "data":{"user_id":"13566284913","article_id":13566284913,"content":"管理员修改内容","title":"管理员修改标题"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)

# # 删除文章（管理员）
# data={"id":0,
#       "type":"article",
#       "subtype":"delete",
#       "data":{"user_id":"13566284913","article_id":1568962356}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/article?token={}".format(token),data=json.dumps(data),headers=headers)

# # 获取评论列表（管理员）
# data={"id":0,
#       "type":"comment",
#       "subtype":"list",
#       "data":{"user_id":"13750687010","article_id":1568546112}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)

# # 增加评论（管理员）
# data={"id":0,
#       "type":"comment",
#       "subtype":"add",
#       "data":{"user_id":"13750687010","article_id":1568546112,"content":"管理员添加评论"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新评论（管理员）
# data={"id":0,
#       "type":"comment",
#       "subtype":"update",
#       "data":{"user_id":"13750687010","comment_id":"f1570b37d305c0b330d2e72fd04fd487","content":"管理员更新评论"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)

# # 删除评论（管理员）
# data={"id":0,
#       "type":"comment",
#       "subtype":"delete",
#       "data":{"user_id":"13750687010","comment_id":"f1570b37d305c0b330d2e72fd04fd487"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/comment?token={}".format(token),data=json.dumps(data),headers=headers)

# # 获取活动列表（管理员）
# data={"id":0,
#       "type":"active",
#       "subtype":"list",
#       "data":{"user_id":"13750687010"}}
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 添加活动（管理员）
# data={
#     "id":1234,
#     "type":"active",
#     "subtype":"add",
#     "data":{
#         "user_id":"13750687010",
#         "title":"测试增加活动",
#         "content":"测试增加活动，召集校友来此一聚",
#         "start_time":"2019-08-24 00:00:00",
#         "end_time":"2019-8-25 0:0:0"
#     }
# }
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新活动（管理员）
# data={
#     "id":1234,
#     "type":"active",
#     "subtype":"update",
#     "data":{
#         "user_id":"13750687010",
#         "active_id":78251505,
#         "title":"测试更新活动2",
#         "content":"测试更新活动2，召集校友来此一聚",
#         "start_time":"2019-08-24 00:00:00",
#         "end_time":"2019-8-25 0:0:0"
#     }
# } ##         "active_id":78251505,
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 加入/退出活动（管理员）
# data={
#     "id":1234,
#     "type":"active",
#     "subtype":"join",  ## exit 退出活动
#     "data":{
#         "user_id":"13750687010",
#         "active_id":59795779,
#     }
# }
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)

# # 删除活动（管理员）
# data={
#     "id":1234,
#     "type":"active",
#     "subtype":"delete",
#     "data":{
#         "user_id":"13750687010",
#         "active_id":78251505,
#     }
# }
# token = "99c9150238fa21051f558ceccad55b8a"
# # response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="http://127.0.0.1:8765/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)

# 获取活动参与成员名单（管理员）
data={
    "id":1234,
    "type":"active",
    "subtype":"member",
    "data":{
        "active_id":78554587,
    }
}
token = "99c9150238fa21051f558ceccad55b8a"
# response = requests.post(url="https://dmt.lcworkroom.cn/api/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)
response = requests.post(url="http://127.0.0.1:8765/admin/active?token={}".format(token),data=json.dumps(data),headers=headers)
print(response.text)