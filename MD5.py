import hashlib
def md5(string:str,salt:str='multimedia'):
    #satl是盐值，默认是multimedia
    string = str(string)
    string = string+salt
    md = hashlib.md5()  # 构造一个md5对象
    md.update(string.encode())
    res = md.hexdigest()
    return res
def md5_bytes(byte:bytes,salt:bytes=b'multimedia'):
    # satl是盐值，默认是b'multimedia'
    byte = bytes(byte)
    byte = byte + salt
    md = hashlib.md5()  # 构造一个md5对象
    md.update(byte)
    res = md.hexdigest()
    return res
if __name__ == "__main__":
    print(md5("nDtg4","D6srg"))