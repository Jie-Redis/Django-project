from ronglian_sms_sdk import SmsSDK
import json

accId = '容联云通讯分配的主账号ID'
accToken = '容联云通讯分配的主账号TOKEN'
appId = '容联云通讯分配的应用ID'


# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '容联云通讯创建的模板ID'
#     mobile = '手机号1,手机号2'
#     datas = ('变量1', '变量2')
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)

#单例模式 对方法进行重写
class Send_sms(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,"_instance"):
            cls._instance = super().__new__(cls,*args,**kwargs)
            cls._instance.sdk = SmsSDK(accId, accToken, appId)
            return cls._instance

    def send_sms(self,tid,mobile,datas):
        resp = self._instance.sdk.sendMessage(tid, mobile, datas)
        result = json.loads(resp)
        if result["statusCode"] == "000000":
            return 1
        else:
            return 0

























