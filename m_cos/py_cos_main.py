# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError

import MD5
import sys,os,configparser
import logging,json

# 腾讯云COSV5Python SDK, 目前可以支持Python2.6与Python2.7以及Python3.x

# pip安装指南:pip install -U cos-python-sdk-v5

# cos最新可用地域,参照https://www.qcloud.com/document/product/436/6224
log_cos = logging.getLogger("COS")
bucket = ""
def Initialize(cfg_path:str,main_path:str):
    """
COS 模块初始化，此函数应在所有函数之前调用
    :param cfg_path: 配置文件地址。
    :param main_path: 程序主目录地址。
    """
    global cf
    cf = configparser.ConfigParser()
    cf.read(cfg_path)

    # 设置用户属性, 包括secret_id, secret_key, region
    # appid已在配置中移除,请在参数Bucket中带上appid。Bucket由bucketname-appid组成
    global secret_id, secret_key, region, token, config, client,bucket
    try:
        secret_id = str(cf.get("COS","secret_id"))  # 替换为用户的secret_id
        secret_key = str(cf.get("COS","secret_key"))  # 替换为用户的secret_key
        region = str(cf.get("COS","region"))  # 替换为用户的region
        token = None  # 使用临时秘钥需要传入Token，默认为空,可不填
        bucket =  str(cf.get("COS","bucket"))
        print("[COS]secret_id:",secret_id)
        print("[COS]secret_key:",secret_key)
        print("[COS]region:", region)
        print("[COS]bucket:", bucket)
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)  # 获取配置对象
        client = CosS3Client(config)
    except Exception as e:
        log_cos.error("UnkownError:",e)
        print("UnkownError:",e)
        log_cos.info("Program Ended")
        sys.exit()
    global Main_filepath
    Main_filepath = main_path
    # print(Main_filepath)
    global server_mode
    server_mode = online_check()
    if server_mode:
        cf.set("COS","server_mode","1")
        print("[COS]Online Server is available")
        log_cos.info("Cos Server is available")
    else:
        cf.set("COS", "server_mode", "0")
        os.makedirs(os.path.join(Main_filepath,"data","local","portrait"),exist_ok=True)
        print("[COS]Online Server is unavailable , using local storage server")
        log_cos.warning("Cos is unavailable , using local storage mode")

    # todo 接下来将对server_mode进行情况处理
    log_cos.info("Module COS loaded")
def online_check()->bool:
    # return False
    response = client.list_buckets()
    buckets = response["Buckets"]["Bucket"]
    for bucket in buckets:
        bucket_name = bucket["Name"]
        if bucket_name == "multimedia-1251848017":
            server_mode = True
            cf.set("COS", "server_mode", "1")
            cf.write(open(os.path.join(Main_filepath,"config.ini"), "w"))
            return True
    else:
        server_mode = False
        cf.set("COS", "server_mode", "0")
        cf.write(open(os.path.join(Main_filepath,"config.ini"), "w"))
        os.makedirs(os.path.join(Main_filepath, "data", "local", "portrait"), exist_ok=True)
        os.makedirs(os.path.join(Main_filepath, "data", "local", "article"), exist_ok=True)
        return False
# 文件流 简单上传
def file_upload(filename:str,key:str,storageclass:str='STANDARD',contentype:str='text/html; charset=utf-8') -> str:
    """
简单上传·文件流模式，以fp的形式打开文件流读取数据并上传。
    :param filename: 要被上传的文件名（完整路径）
    :param key: 对象键（Key）是对象在存储桶中的唯一标识
    :param storageclass: 设置文件的存储类型，STANDARD,STANDARD_IA，默认值：STANDARD
    :param contentype: 内容类型，设置 Content-Type，默认值：text/html; charset=utf-8
    :return 返回被上传的文件的MD5值
    """
    if online_check() == True:
        with open(filename, 'rb') as fp:
            response = client.put_object(
                Bucket=bucket,  # Bucket由bucketname-appid组成
                Body=fp,
                Key=key,
                StorageClass=storageclass,
                ContentType=contentype
            )
            # print(response['ETag'])
            return response['ETag']
    else:
        try:
            with open(filename,'rb') as fp:
                file_data = fp.read()
            with open(os.path.join(Main_filepath,"data","local",key),"wb") as fp2:
                fp2.write(file_data)
            return MD5.md5(file_data,b"")
        except:
            return ""

# 字节流 简单上传
def bytes_upload(body:bytes,key:str) -> str:
    """
简单上传·字节流模式，以bytes的形式上传数据
    :param bucket: Bucket 名称，由 bucketname-appid 构成
    :param body: 文件字节流
    :param key: 对象键（Key）是对象在存储桶中的唯一标识
    :return: 返回被上传的文件的MD5值
    """
    if online_check() == True:
        try:
            response = client.put_object(
                Bucket=bucket,
                Body=body,
                Key=key
            )
        except Exception as e:
            print(type(e))
            log_cos.warning("{}:{}".format(e,type(e)))
            # 容灾处理，上传失败时先放置在本地。
            try:
                with open(os.path.join(Main_filepath, "data", "local", key), "wb") as fp:
                    fp.write(body)
                return MD5.md5_bytes(body, b"")
            except:
                raise e
        else:
            # 容灾处理，本地缓存
            try:
                with open(os.path.join(Main_filepath,"data","local",key),"wb") as fp:
                    fp.write(body)
                return MD5.md5_bytes(body,b"")
            except:
                pass
            print(response['ETag'])
            return response['ETag']
    else:
        try:
            with open(os.path.join(Main_filepath,"data","local",key),"wb") as fp:
                fp.write(body)
            return MD5.md5_bytes(body,b"")
        except:
            raise Exception("<Code>Faild</Code><Message>lalala</Message>",CosServiceError)
# 本地路径 简单上传
def local_upload():
    response = client.put_object_from_local_file(
        Bucket='multimedia-1251848017',
        LocalFilePath='local.txt',
        Key=file_name,
    )
    print(response['ETag'])
# 设置HTTP头部 简单上传
def http_upload():
    response = client.put_object(
        Bucket='multimedia-1251848017',
        Body=b'test',
        Key=file_name,
        ContentType='text/html; charset=utf-8'
    )
    print(response['ETag'])
# 设置自定义头部 简单上传
def custom_upload():
    response = client.put_object(
        Bucket='multimedia-1251848017',
        Body=b'test',
        Key=file_name,
        Metadata={
            'x-cos-meta-key1': 'value1',
            'x-cos-meta-key2': 'value2'
        }
    )
    print(response['ETag'])
# 高级上传接口(推荐)
def high_upload_socket():
    response = client.upload_file(
        Bucket='multimedia-1251848017',
        LocalFilePath='local.txt',
        Key=file_name,
        PartSize=10,
        MAXThread=10
    )
    print(response['ETag'])
# 文件下载 获取文件到本地
def local_dwonload(key:str,outfilename:str)->bool:
    """
文件下载·到本地模式，将cos文件下载至本地指定目录，返回处理结果，True或False
    :param bucket: Bucket 名称，由 bucketname-appid 构成
    :param key: 对象键（Key）是对象在存储桶中的唯一标识
    :param outfilename: 将要保存的文件路径
    :return: 返回处理结果，成功返回True，失败返回False
    """
    if online_check() == True:
        response = client.get_object(
            Bucket=bucket,
            Key=key,
        )
        try:
            response['Body'].get_stream_to_file(outfilename)
            return True
        except Exception as e:
            print(e)
            return False
    else:
        try:
            with open(os.path.join(Main_filepath, "data", "local", key), "rb") as fp:
                file_data = fp.read()
            with open(outfilename,"wb") as fp2:
                fp2.write(file_data)
            return True
        except:
            return False
# 文件下载 获取文件流
def bytes_download(key:str)->bytes:
    """
文件下载·文件流模式，返回bytes类型数据
    :param bucket: Bucket 名称，由 bucketname-appid 构成
    :param key: 对象键（Key）是对象在存储桶中的唯一标识
    :return: 返回文件bytes数据
    """
    if online_check() == True:
        try:
            response = client.get_object(
                Bucket=bucket,
                Key=key,
            )
            fp = response['Body'].get_raw_stream()
            data = fp.read()
        except Exception as e:
            # print(type(e))
            # 容灾处理，若网络取不到则取本地，都取不到再返回默认头像
            try:
                with open(os.path.join(Main_filepath, "data", "local", key),"rb") as fp:
                    file_data = fp.read()
                return file_data
            except:
                raise e
        # print(fp.read(2))
        # 容灾处理，下载时自动缓存
        with open(os.path.join(Main_filepath, "data", "local", key), "wb") as fp2:
            fp2.write(data)
        return data
    else:
        try:
            with open(os.path.join(Main_filepath, "data", "local", key),"rb") as fp:
                file_data = fp.read()
            return file_data
        except:
            raise Exception("<Code>NoSuchKey</Code><Message>The specified key does not exist.</Message>",CosServiceError)
# 文件下载 设置Response HTTP 头部
def http_download():
    response = client.get_object(
        Bucket='zustservice-1251848017',
        Key=file_name,
        ResponseContentType='text/html; charset=utf-8'
    )
    print(response['Content-Type'])
    fp = response['Body'].get_raw_stream()
    print(fp.read(2))
# 文件下载 指定下载范围
def area_download():
    response = client.get_object(
        Bucket='zustservice-1251848017',
        Key=file_name,
        Range='bytes=0-10'
    )
    fp = response['Body'].get_raw_stream()
    print(fp.read())

if __name__ == '__main__':
    Initialize("../config.ini","../")
    file_name = '1180310086.jpg'
    # bucket = 'zustservice-1251848017'
    key = "portrait/1180310086"

    # try:
    #     MD5 = file_upload(bucket=bucket,filename=file_name,key=key)
    #     print("MD5:",MD5)
    # except Exception as e:
    #     print("简单上传·文件流 出错")
    #     print(e)

    try:
        with open(file_name,"rb") as f:
            data = f.read()
        MD5 = bytes_upload(body=data,key=key)
        print("MD5",MD5)
    except Exception as e:
        print("简单上传·字节流 出错")
        print(e)

    try:
        # data = bytes_download(bucket=bucket,key=key)
        result = local_dwonload(key=key,outfilename="./error.jpg")
    except Exception as e:
        msg = str(e)
        code = msg.partition("<Code>")[2].partition("</Code>")[0]
        message = msg.partition("<Message>")[2].partition("</Message>")[0]
        print("出错啦！！！！")
        print(code,message)
    else:
        # string = data.decode("gbk")
        # print(string)
        if result == True:
            print("下载成功")
        else:
            print("下载失败")

# # 文件下载 捕获异常
# try:
#     response = client.get_object(
#         Bucket='zustservice-1251848017',
#         Key='not_exist.txt',
#     )
#     fp = response['Body'].get_raw_stream()
#     print(fp.read(2))
# except CosServiceError as e:
#     print(e.get_origin_msg())
#     print(e.get_digest_msg())
#     print(e.get_status_code())
#     print(e.get_error_code())
#     print(e.get_error_msg())
#     print(e.get_resource_location())
#     print(e.get_trace_id())
#     print(e.get_request_id())