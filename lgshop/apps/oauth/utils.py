from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings



#加密
def generate_openid(openid):

    #创建一个序列化对象
    s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,600)
    #准备要加密的数据
    data = {"openid":"jshgbebencmvevr"}
    #进行序列化
    token = s.dumps(data)
    #返回 因为序列化之后的为字节 要decode
    return token.decode()

#去序列化
def check_openid(access_token_openid):
    #创建一个序列化对象
    s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,600)

    #进行反序列化
    try:
        token = s.loads(access_token_openid)
    except:
        return None
    else:
        return token.get("openid")

