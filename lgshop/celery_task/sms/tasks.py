#创建任务
#导入文件
from celery_task.sms.ronglianyun.send_sms import Send_sms
from celery_task.main import celery_app


#装饰器 保证celery可以识别到任务，其中要设置一个name为任务的名字
@celery_app.task(name="send_sms_code")
def send_sms_code(mobile,sms_code):
    result = Send_sms().send_sms(1,mobile,(sms_code,5))
    return result
