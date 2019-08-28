# Multimedia-Python

[TOC]

# 目录

+ [**Json请求通用格式**](#Json请求通用格式)
+ [**Json返回通用格式**](#Json返回通用格式)
+ [**验证码类**](#验证码类)
  + [登录图片验证码](#登录图片验证码 "生成一个5位字母数字混合的图形验证码")
  + [图片验证码校验](#图片验证码校验 "校验用户输入的验证码是否正确")
  + [注册手机验证码](#注册手机验证码 "发送短信验证码")
+ [**用户类**](#用户类)
  + [账号登录·手机](#账号登录手机 "以手机号作为账号的登录请求")
  + [账号注册·手机](#账号注册手机 "以手机号作为账号的注册请求")
  + [用户信息·获取](#用户信息获取 "获取用户姓名邮箱等信息")
  + [用户信息·更新](#用户信息更新 "更新用户姓名邮箱等信息")
  + [用户头像·上传](#用户头像上传 "上传用户头像")
  + [用户头像·获取](#用户头像获取 "获取用户头像")
+ [**Token类**](#Token类)
  + [心跳doki](#心跳doki "校验并刷新token时效")
+ [**文章类**](#文章类)
  + [增加文章](#增加文章 "发表一篇文章到游客论坛")
  + [更新文章](#更新文章 "更新一篇游客论坛内的文章内容")
  + [删除文章](#删除文章 "删除一篇游客论坛内的文章")
  + [获取文章列表](#获取文章列表 "通过一系列条件检索获取符合条件的文章列表")
+ [**评论类**](#评论类)
  + [增加评论](#增加评论 "给一篇文章发表一条评论")
  + [更新评论](#更新评论 "更新一条评论内容")
  + [删除评论](#删除评论 "删除一条评论")
  + [获取评论列表](#获取评论列表 "通过一系列条件检索获取符合条件的评论列表")
+ [**活动类**](#活动类)
  + [增加活动](#增加活动 "发布一个活动")
  + [更新活动](#更新活动 "更新一个活动内容")
  + [删除活动](#删除活动 "删除一个活动")
  + [获取活动列表](#获取活动列表 "通过一系列条件检索获取符合条件的活动列表")
  + [加入活动](#加入活动 "加入一个活动")
  + [退出活动](#退出活动 "退出一个活动")
  + [获取活动成员列表](#获取活动成员列表 "通过一系列条件检索获取符合条件的活动成员列表")
+ [**全局Status表**](#全局Status表 "所有请求共用的status值")

## **Json请求通用格式**

```python
{
  "id":123456789,
  "type":"xxx",
  "subtype":"xxxx",
  "data":{
      "key":"value"
  }
}
```

## **Json返回通用格式**

```python
{
  "id":123456789,
  "status":0,
  "message":"successful",
  "data":{
      "key":"value"
  }
}
```



> **所需参数介绍：**

|  参数   |                             介绍                             |   调用方   |               样例               |
| :-----: | :----------------------------------------------------------: | :--------: | :------------------------------: |
|   id    |      事件处理id，整型，请求端发送，接收端返回时原样返回      | 请求、返回 |           "id":123456            |
| status  | 返回请求处理状态，请求时status填写0。默认返回0时为请求处理成功，若失败返回错误码 |    返回    |            "status":0            |
| message | 状态简略信息，若成功调用则返回"successful"，失败返回错误信息 |    返回    |      "message":"successful"      |
|  type   |                           请求类型                           |    请求    |          "type":"user"           |
| subtype |                          请求子类型                          |    请求    |        "subtype":"login"         |
|  data   |                   包含附加或返回的请求数据                   | 请求、返回 | "data":{"token":"xxxxxxxxxxxxx"} |

## **验证码类**

#### 登录图片验证码

> **API说明**

此API用于生成一个5位字母数字混合的图形验证码

成功则返回图片的base64数据和一个5位rand值。

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/captcha**

> **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "type":"img",
    "subtype":"generate",
    "data":{}
}
```

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{
        "imgdata":"iVBORw0yrfmx5m7975n32/23Y+cdf1Rv9oA6.....(以下省略)",
        "rand":"CST43"  #随机文本
    }
}
```

> ## 注意

- `id`字段需是整型数据。若是文本型数字数据，返回时自动转换成整数型数据；若是非数字型文本，则返回`-1`。`id`用于让前端在服务繁忙时能够对应服务;  
- Python成功返回时的`imgdata`为验证码base64图片数据，前端获得数据后进行转码再显示;  
- `rand`为随机字符串，前端获得验证码后需要将验证码和`rand`文本MD5加密后传给后端进行验证，`hash = MD5(code+rand)`。  
- 验证码**不区分大小写**，请自行将验证码转换成全部小写再进行hash操作。

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":1000, # 错误码
  "message":"验证码文件创建失败",
  "data":{},
}
```

- `status`传递的错误码类型为整型。具体的错误码详见`全局status表`和`局部status表`。

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -3     |
| -2     |
| -1     |

#### 图片验证码校验

> **API说明**

此API用于校验用户输入的验证码是否正确，**在目前版本中，此API暂时用不到**

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/captcha**

> **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "type":"img",
    "subtype":"validate",
    "data":{"hash":"asddwfw……"}
}
```

> **data字段表**

| 参数 | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |           备注            |
| :--: | :------: | :------: | :------: | :------: | :------------------------------: | :-----------------------: |
| hash |          |          |  string  |    32    | cffb7f1eb316fd45bbfbd43082e36f9c | hash = MD5(imgcode + rand |



> ## 注意

- `hash`字段的数据要求是用户填写的验证码内容与rand文本进行MD5加密获得。即`hash = MD5(code + rand)`
- 验证码**不区分大小写**，请自行将验证码转换成全部小写再进行hash操作。

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{}
}
```

> **Python端返回失败处理情况**

```python
{
  "id":请求时的ID,
  "status":-1, # 验证码hash值不匹配
  "message":"验证码hash值不匹配",
  "data":{},
}
```

- `status`传递的错误码类型为整型。具体的错误码详见`全局status表`和`局部status表`。

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -404   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message            | 内容                                           |
| ------ | ------------------ | ---------------------------------------------- |
| 100    | Error captcha hash | 校验失败，验证码hash值不匹配（包括验证码过期） |

#### 注册手机验证码

> **API说明**

此API用于以手机号作为账号进行注册时发送短信验证码

成功则向指定手机发送短信，并返回一个5位`rand`值，用于用户注册时

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/captcha**

> **POST发送请求的json文本**

```python
{
    "id":事件ID,
    "type":"sms",
    "subtype":"generate",
    "data":{
        "phone":"137xxxxxxxx"
        }
}
```

> **data字段表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |                         备注                          |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------------------------------------------: |
| phone |          |          |  string  |    11    |           13750687010            |                  中国大陆11位手机号                   |
| hash  |          |    √     |  string  |    32    | cffb7f1eb316fd45bbfbd43082e36f9c | **该字段目前不使用**<br />`hash = MD5(imgcode + rand` |

> ## 注意

- `phone`字段需用文本型传递，且只能为中国大陆手机号，不支持国外手机号
- `hash`字段的数据要求是用户填写的验证码内容与rand文本进行MD5加密获得。即`hash = MD5(code + rand)`

> **Python端返回成功处理情况**

```python
{
   "id":请求时的ID,
   "status":0,
   "message":"successful",
   "data":{
       "rand":"DSf4s"
   }
}
```

> ## 注意：

- 新版本里将返回数据`data`中的`code`字段删除了。   
- `rand`为随机字符串，前端获得验证码后需要将验证码和rand文本进行MD5加密后传给后端端进行验证，`hash = MD5(code+rand)`，此hash用于账号注册。
- **手机验证码的时效为3min，由后端处理。验证码超时后端会返回`status = -4`的错误。**

> **Python端返回失败处理情况**

```python
{
     "id":请求时的ID,
     "status":1016,  #错误码
     "message":"手机号格式错误",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -404   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status                                                       |
| ------------------------------------------------------------ |
| 具体错误码请看腾讯云[短信错误码](https://cloud.tencent.com/document/product/382/3771 "腾讯短信API文档") |

> ## 注意

- `status`传递的错误码类型为整型。具体的错误码参照**腾讯云短信服务API文档**。
  [短信错误码](https://cloud.tencent.com/document/product/382/3771 "腾讯短信API文档")

## 用户类

#### 账号登录·手机

> **API说明**

此API用于以手机号作为登录凭证时的登录请求

成功返回token值

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/user/login**

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"login",
    "subtype":"pass",
    "data":{
        "phone":"13750687010",
        "pass":"wlc570Q0",
        "enduring":False,
    }
}
```

> **data字段表**

|   参数   | 可否为空 | 可否缺省 | 数据类型 |  字段长度  |    例子     |                             备注                             |
| :------: | :------: | :------: | :------: | :--------: | :---------: | :----------------------------------------------------------: |
|  phone   |          |          |  string  |     11     | 13750687010 |                       登录账号(手机号)                       |
|   pass   |          |          |  string  | 由前端决定 |  wlc570Q0   |                           登录密码                           |
| enduring |          |    √     |   int    |     1      |    False    | 是否为长效登录，1为长效，0为非长效（无操作10min）<br />**默认为0** |

> ## 注意

- `phone`字段需用文本型传递
- `pass`字段的长度由前端限制，后端只取其MD5值进行判断

> **Python端返回成功处理情况**

```python
{
    "id": 1234,
    "status": 0, 
    "message": "Successful", 
    "data": {
        "token": "debc454ea24827b67178482fd73f37c3"
    }
}
```

> ## 注意：

- 获取的`token`用于后期所有需要用户验证的请求操作。  
- 账号每登录一次即可获得一个`token`
- 一个账号同时获得10个以上的`token`时，自动删除早期的`token`，维持token数在10以内
- 获得的`token`未被用于任何操作超过`10min`后将被自动删除（设置为长效token的除外）
- 若`enduring`传递了非`int`类型数据，则自动为`0`

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":101,  #错误码
     "message":"Error password",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message               | 内容                     |
| ------ | --------------------- | ------------------------ |
| 100    | Incorrect user        | 无该账号记录             |
| 101    | Error password        | 用户输入的密码错误       |
| 200    | Invalid record number | 有两条及以上该账号的数据 |
| 300    | Add token failed      | 获取token失败            |

#### 账号注册·手机

> **API说明**

此API用于以手机号作为登录凭证时的注册请求

成功返回token值

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/user/register**

> **POST发送请求的json文本**

```python
{
    "id":0,
    "status":0,
    "type":"register",
    "subtype":"phone",
    "data":{
        "phone":"13750687010",
        "hash":"cffb7f1eb316fd45bbfbd43082e36f9c",
        "pass":"wlc570Q0"
    }
}
```

> **data字段表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 |  字段长度  |               例子               |                             备注                             |
| :---: | :------: | :------: | :------: | :--------: | :------------------------------: | :----------------------------------------------------------: |
| phone |          |          |  string  |     11     |           13750687010            |                       登录账号(手机号)                       |
| hash  |          |          |  string  |     32     | cffb7f1eb316fd45bbfbd43082e36f9c | 此hash由手机验证码的code与rand进行MD5加密获得<br />`hash=MD5(smscode+rand)` |
| pass  |          |          |  string  | 由前端决定 |             wlc570Q0             |                           登录密码                           |

> ## 注意

- `phone`字段需用文本型传递
- `pass`字段的长度由前端限制，后端只取其MD5值进行判断

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":101,  #错误码
     "message":"Phone number existed",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message                    | 内容                     |
| ------ | -------------------------- | ------------------------ |
| 100    | Incorrect user data        | 创建账号失败             |
| 101    | Phone number existed       | 手机号已存在             |
| 102    | Incorrect user information | 创建用户资料失败         |
| 200    | Invalid record number      | 有两条及以上该账号的数据 |
| 400    | Error hash                 | Hash校验文本错误         |

#### 用户信息·获取

> **API说明**

此API用于通过token值获取对应用户信息

> **API类型**

**请求类型：`GET`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/user/info?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **Python端返回成功处理情况**

```python
{
    "id": -1, 
    "status": 0, 
    "message": "Successful", 
    "data": {
        "phone": "13750687010", 
        "name": "\u738b\u51cc\u8d85", 
        "nickname": "FatBallFish", 
        "email": "893721708@qq.com", 
        "level": 1
    }
}
```

> **Python端返回失败处理情况**

```python
{
    "id": -1, 
    "status": 1, 
    "message": "Error Token", 
    "data": {}
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -100   |

> **局部status表**

| status | message     | 内容        |
| :----- | ----------- | ----------- |
| 1      | Error Token | token不正确 |

#### 用户信息·更新

> **API说明**

此API用于更新用户信息

成功返回token值

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/user/info?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":0,
    "type":"info",
    "subtype":"update",
    "data":{
        "phone":"13750687010",
        "name":"王凌超",
        "nickname":"FatBallFish",
        "email":"893721708@qq.com"}
}
```

> **data字段表**

|   参数   | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注       |
| :------: | :------: | :------: | :------: | :------: | :------------------------------: | :--------------: |
|  phone   |          |          |  string  |    11    |           13750687010            | 登录账号(手机号) |
|   name   |    √     |    √     |  string  |    20    | cffb7f1eb316fd45bbfbd43082e36f9c |                  |
| nickname |    √     |    √     |  string  |    20    |             wlc570Q0             |     登录密码     |
|  email   |    √     |    √     |  string  |    50    |         893721708@qq.com         |     邮箱地址     |
|  level   |          |    √     |   int    |          |                1                 |     用户等级     |

> ## 注意

- `phone`用作检验机制，不可被修改
- `level`字段若被使用则必须传递数值，不能为空

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":101,  #错误码
     "message":"Phone number existed",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

#### 用户头像·上传

> **API说明**

此API用于上传用户的头像图片

成功返回头像的url地址

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/protrait?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"portrait",
    "subtype":"upload",
    "data":{
        "base64":img_base64  # string型
    }
}
```

> **data字段表**

|  参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |                   例子                    |                             备注                             |
| :----: | :------: | :------: | :------: | :------: | :---------------------------------------: | :----------------------------------------------------------: |
| base64 |          |          |  string  |          | /9j/4AAQSkZJRgABAQEA.......(长度过长省略) | 图片的base64格式文本，前端尽量限制图片大小在1M以下，否则容易卡顿，3M以上请求容易失败 |

> ## 注意

- `base64`可选择是否带有base头标识，实际不影响。标识例子：`data:image/jpg;base64,`
- 若该用户原先已有头像，新头像将自动覆盖原有头像，原头像被删除。

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0,
    "message": "Successful", 
    "data": {
        "url": "./api/get/portrait/13750687010"
    }
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":-100,  #错误码
     "message":"Missing necessary args",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

#### 用户头像·获取

> **API说明**

此API用于通过token值获取对应用户信息

> **API类型**

**请求类型：`GET`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/get/portrait/<user_id>**

> **url 参数表**

|  参数   | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |    例子     |  备注  |
| :-----: | :------: | :------: | :------: | :------: | :---------: | :----: |
| user_id |          |          |  string  |    11    | 13750687010 | 用户id |

> **API例子**

**https://dmt.lcworkroom.cn/api/get/portrait/13750687010**

> **Python端返回成功处理情况**

```python
二进制型图片数据（bytes）
```

> ## 注意

+ 前端调用此api时，直接将api地址写在`src`中即可，例如：<br>`<img src="https://dmt.lcworkroom.cn/get/portrait/1180310086">`

> **Python端返回失败处理情况**

```python
视情况返回以下三种图片：
1.在服务器域名外访问此api，返回“ban.jpg”，提示“多媒体站内图片，禁止外部引用”
2.输入的user_id不存在但格式正确返回“default.jpg”，即默认头像
3.输入的user_id格式出错（出现非数字字符），返回“error.jpg”，提示“参数传递错误，无法获取图片”
```

> ## 注意

- 调用此api时，请注意当前api所在地址，若非`https://dmt.lcworkroom.cn`或`http://localhost`这两个根域名的话，将会返回`ban.jpg`

> **所用到的全局status**

无

## **Token类**

#### 心跳doki

> **API说明**

此API用于检验token是否有效，若有效并刷新token有效时间。

> **API类型**

**请求类型：`GET`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/user/doki?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **Python端返回成功处理情况**

```python
{
    "id": id, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
    "id": -1, 
    "status": 1,
    "message": "Token not existed", 
    "data": {}
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -100   |

> **局部status表**

| status | message              | 内容             |
| :----- | -------------------- | ---------------- |
| 1      | Token not existed    | Token不存在      |
| 200    | Invalid token number | 同一Token大于2条 |



## **文章类**

#### 增加文章

> **API说明**

此API用于增加论坛文章内容

成功返回`article_id`

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/article?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"article",
    "subtype":"add",
    "data":{
        "title":"测试文章",
        "content":"王凌超"}
}
```

> **data字段表**

|  参数   | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |       例子       |   备注   |
| :-----: | :------: | :------: | :------: | :------: | :--------------: | :------: |
|  title  |          |          |  string  |   255    |     测试文章     |  文章id  |
| content |          |          |  string  |          | 这是一篇测试文章 | 文章内容 |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {
        "article_id":1565920055
    }
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":-200,  #错误码
     "message":"Failure to operate database",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

#### 更新文章

> **API说明**

此API用于更新论坛文章内容

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/article?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"article",
    "subtype":"update",
    "data":{
        "article_id":1565920055,
        "content":"王凌超"}
}
```

> **data字段表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子                |   备注   |
| :--------: | :------: | :------: | :------: | :------: | :-------------------------------: | :------: |
| article_id |          |          |  bigint  |    10    |            1565920055             |  文章id  |
|  content   |          |          |  string  |          | 这是一篇测试文章,测试一下更新效果 | 文章内容 |

> ## 注意

- `article_id`用作检验机制，不可被修改

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":100,  #错误码
     "message":"Error article_id",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message          | 内容                                 |
| :----- | ---------------- | ------------------------------------ |
| 100    | Error article_id | 文章id错误，很有可能不存在           |
| 101    | Error user_id    | 文章作者id与当前登录id不一致或无权限 |

#### 删除文章

> **API说明**

此API用于删除论坛文章

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/article?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"article",
    "subtype":"delete",
    "data":{
        "article_id":1565920055}
}
```

> **data字段表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |    例子    |  备注  |
| :--------: | :------: | :------: | :------: | :------: | :--------: | :----: |
| article_id |          |          |  bigint  |    10    | 1565920055 | 文章id |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":100,  #错误码
     "message":"Error article_id",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message          | 内容                                 |
| :----- | ---------------- | ------------------------------------ |
| 100    | Error article_id | 文章id错误，很有可能不存在           |
| 101    | Error user_id    | 文章作者id与当前登录id不一致或无权限 |

#### 获取文章列表

> **API说明**

此API用于获取游客论坛文章列表

> **API类型**

**请求类型：`GET`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/get/article/list**

> **url 参数表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 | 默认值           |               例子               |                             备注                             |
| :--------: | :------: | :------: | :------: | :------: | ---------------- | :------------------------------: | :----------------------------------------------------------: |
|   token    |          |          |  string  |    32    |                  | debc454ea24827b67178482fd73f37c3 |                      由登录api返回获得                       |
|  keywords  |    √     |    √     |  string  |          |                  |               测试               | 搜索关键字，设置后将以此关键字模糊匹配title和content字段内容，模糊匹配 |
| article_id |    √     |    √     |   int    |    10    |                  |            1565926081            |                       文章id，精确匹配                       |
|   title    |    √     |    √     |  string  |          |                  |             测试文章             |                      文章标题，模糊匹配                      |
|  content   |    √     |    √     |  string  |          |                  |               这是               |                      文章内容，模糊匹配                      |
|   order    |    √     |    √     |  string  |          | update_time DESC |    title ASC,update_time DESC    |     排序规则，使用SQL语句，为空则默认以更新时间进行排序      |
|   start    |    √     |    √     |   int    |          | 0                |                0                 |                  记录索引开始，默认起始为 0                  |
|    num     |    √     |    √     |   int    |          | 50               |                10                |                   返回记录数，默认返回50条                   |

> ## 注意

- 只传递`token`参数则返回所有文章
- 如果`keywords`不为空则优先使用`keywords`，`article_id`、`title`、`content`则被忽略；
- `keywords`用于`title`和`content`的并集查询，模糊匹配；
- `article_id`、`title`、`content`可交集查询；
- `order`中可用于排序的字段有`article_id`, `user_id`, `title`,`content`,`create_time`, `update_time`;
- `order`排序方法有：升序`asc`、降序`desc`，大小写不区分。多条件排序时用英文半角`,`分割
- 当实际记录数小于`num`的值时，只返回实际记录数量的记录

> **URL例程**

**https://dmt.lcworkroom.cn/api/get/article/list?token=99c9150238fa21051f558ceccad55b8a**

> **Python端返回成功处理情况**

```python
{
    "id": -1, 
    "status": 0, 
    "message": "successful", 
    "data": {
        "num": 1, 
        "list": [
            {"article_id": 1565926081, 
             "user_id": "13750687010", 
             "title": "测试文章", 
             "content": "这是一篇测试文章", 
             "create_time": "2019-08-16 11:28:01", 
             "update_time": "2019-08-16 11:28:01"}
        ]
    }
}
```

> **Python端返回失败处理情况**

```python
{
    "id": -1, 
    "status": -101, 
    "message": "Error Token", 
    "data": {}
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -203   |
| -200   |
| -101   |
| -100   |

> **局部status表**

| status | message     | 内容              |
| :----- | ----------- | ----------------- |
| 100    | Error Order | 排序规则错误      |
| 101    | Error num   | num值错误，不能<1 |



## **评论类**

#### 增加评论

> **API说明**

此API用于增加论坛文章的评论内容

成功返回`article_id`、`comment_id`、`father_id`

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/comment?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"comment",
    "subtype":"add",
    "data":{
        "article_id":1565926081,
        "content":"这是一条用API请求的子级评论",
        "father_id":"76bd7b76fcd0b23f3d171f39b416d936"
    }
}
```

> **data字段表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |                        备注                         |
| :--------: | :------: | :------: | :------: | :------: | :------------------------------: | :-------------------------------------------------: |
| article_id |          |          |   int    |    10    |            1565926081            |                       文章id                        |
|  content   |          |          |  string  |          |         这是一篇测试文章         |                      文章内容                       |
| father_id  |    √     |    √     |  string  |    32    | 76bd7b76fcd0b23f3d171f39b416d936 | 父评论id（MD5加密文本），若为空则为根评论，默认为空 |

> ## 注意

- `article_id`、`father_id`用作检验机制，不可被修改

> **Python端返回成功处理情况**

```python
{
    "id": 1234,
    "status": 0, 
    "message": "Successful", 
    "data": {
        "article_id": 1565926081, 
        "comment_id": "354b6ded0748cd837d0ebf06230b9770"
    }
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":100,  #错误码
     "message":"Error article_id",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message          | 内容                       |
| :----- | ---------------- | -------------------------- |
| 100    | Error article_id | 文章id错误，很有可能不存在 |
| 101    | Error father_id  | 父评论错误，很有可能不存在 |



#### 更新评论

> **API说明**

此API用于更新论坛文章评论内容

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/comment?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"comment",
    "subtype":"update",
    "data":{
        "comment_id":"d757d9ea4c9c1860299a0341524a6a7d",
        "content":"这是一条用API更新的子级评论"
    }
}
```

> **data字段表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子                |   备注   |
| :--------: | :------: | :------: | :------: | :------: | :-------------------------------: | :------: |
| comment_id |          |          |  string  |    32    | d757d9ea4c9c1860299a0341524a6a7d  |  评论id  |
|  content   |          |          |  string  |          | 这是一篇测试文章,测试一下更新效果 | 文章内容 |

> ## 注意

- `comment_id`用作检验机制，不可被修改

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":100,  #错误码
     "message":"Error article_id",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message          | 内容                                 |
| :----- | ---------------- | ------------------------------------ |
| 100    | Error comment_id | 评论id错误，很有可能不存在           |
| 101    | Error user_id    | 评论作者id与当前登录id不一致或无权限 |

#### 删除评论

> **API说明**

此API用于删除论坛评论文章

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/comment?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":0,
    "type":"comment",
    "subtype":"delete",
    "data":{
        "comment_id":"a301c03e1248eabf83785b5548d603ec"}
}
```

> **data字段表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |  备注  |
| :--------: | :------: | :------: | :------: | :------: | :------------------------------: | :----: |
| comment_id |          |          |  string  |    32    | a301c03e1248eabf83785b5548d603ec | 评论id |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":100,  #错误码
     "message":"Error article_id",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message          | 内容                                 |
| :----- | ---------------- | ------------------------------------ |
| 100    | Error comment_id | 评论id错误，很有可能不存在           |
| 101    | Error user_id    | 评论作者id与当前登录id不一致或无权限 |



#### 获取评论列表

> **API说明**

此API用于获取游客论坛文章评论列表

> **API类型**

**请求类型：`GET`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/get/comment/list**

> **url 参数表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 | 默认值           |               例子               |                        备注                         |
| :--------: | :------: | :------: | :------: | :------: | ---------------- | :------------------------------: | :-------------------------------------------------: |
|   token    |          |          |  string  |    32    |                  | debc454ea24827b67178482fd73f37c3 |                  由登录api返回获得                  |
| article_id |          |          |   int    |    10    |                  |            1565926081            |                  文章id，精确匹配                   |
| comment_id |    √     |    √     |  string  |    32    |                  | d757d9ea4c9c1860299a0341524a6a7d |                  评论id，精确匹配                   |
| father_id  |    √     |    √     |  string  |    32    |                  | a301c03e1248eabf83785b5548d603ec |                 父评论id，精确匹配                  |
|  content   |    √     |    √     |  string  |          |                  |         这是一条评论内容         |                 评论内容，模糊匹配                  |
|   order    |    √     |    √     |  string  |          | update_time DESC |    title ASC,update_time DESC    | 排序规则，使用SQL语句，为空则默认以更新时间进行排序 |
|   start    |    √     |    √     |   int    |          | 0                |                0                 |             记录索引开始，默认起始为 0              |
|    num     |    √     |    √     |   int    |          | 50               |                10                |              返回记录数，默认返回50条               |

> ## 注意

- 只传递`token`和`article_id`参数则返回该文章的所有根评论，不含子评论。
- `article_id`、`comment_id`、`father_id`、`content`可交集查询；
- `order`中可用于排序的字段有`article_id`, `user_id`,`comment_id`、`father_id`、,`content`,`create_time`, `update_time`;
- `order`排序方法有：升序`asc`、降序`desc`，大小写不区分。多条件排序时用英文半角`,`分割
- 当实际记录数小于`num`的值时，只返回实际记录数量的记录

> **URL例程**

**https://dmt.lcworkroom.cn/api/get/comment/list?token=99c9150238fa21051f558ceccad55b8a&article_id=1565926081**

> **Python端返回成功处理情况**

```python
{
    "id": -1,
    "status": 0, 
    "message": "successful", 
    "data": {
        "num": 2, 
        "list": [
            {
                "article_id": 1565926081, 
                "comment_id": "76bd7b76fcd0b23f3d171f39b416d936", 
                "father_id": "", 
                "user_id": "13750687010", 
                "content": "这是一条更新过的评论", 
                "create_time": "2019-08-18 09:41:41", 
                "update_time": "2019-08-18 11:08:43"
            }, 
            {
                "article_id": 1565926081, 
                "comment_id": "1aa6ddf68bea87f2305dd9fd5d3bb2c8", 
                "father_id": "", 
                "user_id": "13750687010", 
                "content": "这是一条测试评论", 
                "create_time": "2019-08-18 09:32:16", 
                "update_time": "2019-08-18 09:32:16"
            }
        ]
    }
}
```

> **Python端返回失败处理情况**

```python
{
    "id": -1, 
    "status": -101, 
    "message": "Error Token", 
    "data": {}
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -203   |
| -200   |
| -101   |
| -100   |

> **局部status表**

| status | message          | 内容              |
| :----- | ---------------- | ----------------- |
| 100    | Error order      | 排序规则错误      |
| 101    | Error num        | num值错误，不能<1 |
| 102    | Error article_id | 错误的文章id      |



## **活动类**

#### 增加活动

> **API说明**

此API用于增加论坛活动

成功返回`active_id`

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/active?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"active",
    "subtype":"add",
    "data":{
        "title":"校友召集令",
        "content":"恰逢更名时机，召集校友来此一聚",
        "start_time":"2019-08-24 00:00:00",
        "end_time":"2019-8-25 0:0:0"
    }
}
```

> **data字段表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |        例子         |                     备注                     |
| :--------: | :------: | :------: | :------: | :------: | :-----------------: | :------------------------------------------: |
|   title    |          |          |  string  |   255    |      测试文章       |                    文章id                    |
|  content   |          |          |  string  |          |  这是一篇测试文章   |                   文章内容                   |
| start_time |          |          | datetime |          | 2019-08-24 00:00:00 | 请按照标准的时间格式文本进行传递，否则会报错 |
|  end_time  |          |          | datetime |          | 2019-08-25 00:00:00 | 请按照标准的时间格式文本进行传递，否则会报错 |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {
        "active_id":78554587
    }
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":-200,  #错误码
     "message":"Failure to operate database",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message                       | 内容                             |
| :----- | ----------------------------- | -------------------------------- |
| 102    | Error format or data for time | 开始时间或结束时间格式或数据错误 |

#### 更新活动

> **API说明**

此API用于更新论坛活动

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/active?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"active",
    "subtype":"update",
    "data":{
        "active_id":78554587,
        "title":"校友召集令",
        "content":"恰逢更名时机，召集校友来此一聚，更新活动内容",
        "start_time":"2019-08-25 00:00:00",
        "end_time":"2019-08-26 00:00:00"
    }
}
```

> **data字段表**

|    参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |        例子         |                     备注                     |
| :--------: | :------: | :------: | :------: | :------: | :-----------------: | :------------------------------------------: |
| active_id  |          |          |   int    |    8     |      78554587       |                    活动id                    |
|   title    |          |          |  string  |   255    |      测试文章       |                    文章id                    |
|  content   |          |          |  string  |          |  这是一篇测试文章   |                   文章内容                   |
| start_time |          |          | datetime |          | 2019-08-24 00:00:00 | 请按照标准的时间格式文本进行传递，否则会报错 |
|  end_time  |          |          | datetime |          | 2019-08-25 00:00:00 | 请按照标准的时间格式文本进行传递，否则会报错 |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":-200,  #错误码
     "message":"Failure to operate database",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message                       | 内容                                   |
| :----- | ----------------------------- | -------------------------------------- |
| 100    | Error active_id               | 错误的活动id                           |
| 101    | Error user_id                 | 活动发起者id与当前登录id不一致或无权限 |
| 102    | Error format or data for time | 开始时间或结束时间格式或数据错误       |

#### 删除活动

> **API说明**

此API用于删除论坛活动

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/active?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"active",
    "subtype":"delete",
    "data":{
        "active_id":86889745
    }
}
```

> **data字段表**

|   参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |   例子   |  备注  |
| :-------: | :------: | :------: | :------: | :------: | :------: | :----: |
| active_id |          |          |   int    |    8     | 78554587 | 活动id |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":-200,  #错误码
     "message":"Failure to operate database",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message         | 内容                                   |
| :----- | --------------- | -------------------------------------- |
| 100    | Error active_id | 错误的活动id                           |
| 101    | Error user_id   | 活动发起者id与当前登录id不一致或无权限 |

#### 获取活动列表

> **API说明**

此API用于获取论坛活动列表

> **API类型**

**请求类型：`GET`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/get/active/list**

> **url 参数表**

|   参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 | 默认值           |               例子               |                             备注                             |
| :-------: | :------: | :------: | :------: | :------: | ---------------- | :------------------------------: | :----------------------------------------------------------: |
|   token   |          |          |  string  |    32    |                  | debc454ea24827b67178482fd73f37c3 |                      由登录api返回获得                       |
| keywords  |    √     |    √     |  string  |          |                  |               测试               | 搜索关键字，设置后将以此关键字模糊匹配title和content字段内容，模糊匹配 |
| active_id |    √     |    √     |   int    |    8     |                  |             78554587             |                       活动id，精确匹配                       |
|   title   |    √     |    √     |  string  |          |                  |             测试文章             |                      活动标题，模糊匹配                      |
|  content  |    √     |    √     |  string  |          |                  |               这是               |                      活动内容，模糊匹配                      |
|   order   |    √     |    √     |  string  |          | update_time DESC |    title ASC,update_time DESC    |     排序规则，使用SQL语句，为空则默认以更新时间进行排序      |
|   start   |    √     |    √     |   int    |          | 0                |                0                 |                  记录索引开始，默认起始为 0                  |
|    num    |    √     |    √     |   int    |          | 50               |                10                |                   返回记录数，默认返回50条                   |

> ## 注意

- 只传递`token`参数则返回所有活动
- 如果`keywords`不为空则优先使用`keywords`，`article_id`、`title`、`content`则被忽略；
- `keywords`用于`title`和`content`的并集查询，模糊匹配；
- `active_id`、`title`、`content`可交集查询；
- `order`中可用于排序的字段有`active_id`, `user_id`, `title`,`content`,`start_time`,`end_time`,`create_time`, `update_time`;
- `order`排序方法有：升序`asc`、降序`desc`，大小写不区分。多条件排序时用英文半角`,`分割
- 当实际记录数小于`num`的值时，只返回实际记录数量的记录

> **URL例程**

**https://dmt.lcworkroom.cn/api/get/active/list?token=99c9150238fa21051f558ceccad55b8a**

> **Python端返回成功处理情况**

```python
{
    "id": -1, 
    "status": 0, 
    "message": "successful", 
    "data": {
        "num": 1, 
        "list": [
            {"active_id": 78554587, 
             "user_id": "13750687010", 
             "title": "校友召集令", 
             "content": "恰逢更名时机，召集校友来此一聚，更新活动内容", 
             "start_time": "2019-08-25 00:00:00", 
             "end_time": "2019-08-26 00:00:00", 
             "create_time": "2019-08-24 15:29:57", 
             "update_time": "2019-08-24 15:29:57"}
        ]
    }
}
```

> **Python端返回失败处理情况**

```python
{
    "id": -1, 
    "status": -101, 
    "message": "Error Token", 
    "data": {}
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -203   |
| -200   |
| -101   |
| -100   |

> **局部status表**

| status | message     | 内容              |
| :----- | ----------- | ----------------- |
| 100    | Error Order | 排序规则错误      |
| 101    | Error num   | num值错误，不能<1 |

#### 加入活动

> **API说明**

此API用于用户加入活动

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/active?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"active",
    "subtype":"join",
    "data":{
        "active_id":78554587,
    }
}
```

> **data字段表**

|   参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |   例子   |  备注  |
| :-------: | :------: | :------: | :------: | :------: | :------: | :----: |
| active_id |          |          |   int    |    8     | 78554587 | 活动id |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":-200,  #错误码
     "message":"Failure to operate database",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message         | 内容                       |
| :----- | --------------- | -------------------------- |
| 100    | Error active_id | 错误的活动id，可能并不存在 |
| 102    | Already joined  | 用户已加入此活动           |

#### 退出活动

> **API说明**

此API用于用户加入活动

> **API类型**

**请求类型：`POST`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/active?token=**

> **url 参数表**

| 参数  | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |               例子               |       备注        |
| :---: | :------: | :------: | :------: | :------: | :------------------------------: | :---------------: |
| token |          |          |  string  |    32    | debc454ea24827b67178482fd73f37c3 | 由登录api返回获得 |

> **POST发送请求的json文本**

```python
{
    "id":1234,
    "type":"active",
    "subtype":"exit",
    "data":{
        "active_id":78554587,
    }
}
```

> **data字段表**

|   参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 |   例子   |  备注  |
| :-------: | :------: | :------: | :------: | :------: | :------: | :----: |
| active_id |          |          |   int    |    8     | 78554587 | 活动id |

> **Python端返回成功处理情况**

```python
{
    "id": 1234, 
    "status": 0, 
    "message": "Successful", 
    "data": {}
}
```

> **Python端返回失败处理情况**

```python
{
     "id":1234,
     "status":-200,  #错误码
     "message":"Failure to operate database",
     "data":{},
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -200   |
| -101   |
| -100   |
| -3     |
| -2     |
| -1     |

> **局部status表**

| status | message                       | 内容                                                       |
| :----- | ----------------------------- | ---------------------------------------------------------- |
| 100    | Error active_id               | 错误的活动id，可能并不存在                                 |
| 101    | Error user_id                 | 活动参与者id与当前登录id不一致或无权限或该用户未加入此活动 |
| 102    | Error format or data for time | 开始时间或结束时间格式或数据错误                           |

#### 获取活动成员列表

> **API说明**

此API用于获取论坛活动列表

> **API类型**

**请求类型：`GET`**

> **API地址：**

**https://dmt.lcworkroom.cn/api/get/active/member**

> **url 参数表**

|   参数    | 可否为空 | 可否缺省 | 数据类型 | 字段长度 | 默认值           |               例子               |                        备注                         |
| :-------: | :------: | :------: | :------: | :------: | ---------------- | :------------------------------: | :-------------------------------------------------: |
|   token   |          |          |  string  |    32    |                  | debc454ea24827b67178482fd73f37c3 |                  由登录api返回获得                  |
| active_id |    √     |    √     |   int    |    8     |                  |             78554587             |                  活动id，精确匹配                   |
|   order   |    √     |    √     |  string  |          | update_time DESC |          join_time ASC           | 排序规则，使用SQL语句，为空则默认以加入时间升序排序 |
|   start   |    √     |    √     |   int    |          | 0                |                0                 |             记录索引开始，默认起始为 0              |
|    num    |    √     |    √     |   int    |          | 50               |                10                |              返回记录数，默认返回50条               |

> ## 注意

- `order`中可用于排序的字段有`active_id`, `user_id`, `title`,`content`,`start_time`,`end_time`,`create_time`, `update_time`;
- `order`排序方法有：升序`asc`、降序`desc`，大小写不区分。多条件排序时用英文半角`,`分割
- 当实际记录数小于`num`的值时，只返回实际记录数量的记录

> **URL例程**

**https://dmt.lcworkroom.cn/api/get/active/member?token=99c9150238fa21051f558ceccad55b8a&active_id=78554587**

> **Python端返回成功处理情况**

```python
{
    "id": -1, 
    "status": 0, 
    "message": "successful", 
    "data": {
        "num": 1, 
        "list": [
            "13750687010"
        ]
    }
}
```

> **Python端返回失败处理情况**

```python
{
    "id": -1, 
    "status": -101, 
    "message": "Error Token", 
    "data": {}
}
```

> **所用到的全局status**

全局参数详情请看[全局Status表](#全局Status表)

| status |
| ------ |
| -203   |
| -200   |
| -101   |
| -100   |

> **局部status表**

| status | message         | 内容         |
| :----- | --------------- | ------------ |
| 100    | Error Order     | 排序规则错误 |
| 102    | Error active_id | 错误的活动id |

## **全局Status表**

**所有的全局status值皆小于0**

**大于 0 的status值皆为请求局部status值**

| 参数 |              Message               |                内容                 | 请求类型  |
| :--: | :--------------------------------: | :---------------------------------: | --------- |
|  0   |             successful             |            函数处理正确             | POST、GET |
|  -1  |           Error JSON key           |         json文本必需key缺失         | POST      |
|  -2  |          Error JSON value          |          json文本value错误          | POST      |
|  -3  |           Error data key           |        data数据中必需key缺失        | POST      |
|  -4  |             Error Hash             |          Hash校验文本错误           | POST      |
| -100 |       Missing necessary args       |       api地址中缺少token参数        | POST、GET |
| -101 |            Error token             |             token不正确             | POST、GET |
| -102 |  Get userid failed for the token   |      使用该token获取userid失败      | POST、GET |
| -200 |    Failure to operate database     | 数据库操作失败，检查SQL语句是否正确 | POST、GET |
| -201 | Necessary key-value can't be empty |        关键键值对值不可为空         | POST      |
| -202 |  Missing necessary data key-value  |          缺少关键的键值对           | POST      |
| -203 |       Arg's value type error       |         键值对数据类型错误          | POST      |
| -204 |         Arg's value error          |           键值对数据错误            | POST      |
| -404 |           Unknown Error            |           未知的Redis错误           | POST      |

------

- `status`传递的错误码类型为整型。

- 手机验证码相关的错误码详见[短信错误码](https://cloud.tencent.com/document/product/382/3771 "腾讯短信API文档")

