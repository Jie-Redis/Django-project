from django.shortcuts import render
from django import views
from django.views import View
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from verifications.libs.ronglianyun.send_sms import Send_sms
import random
from celery_task.sms.tasks import send_sms_code


# 图形验证码
class ImageCodeView(View):
    # 定义接口
    def get(self, request, uuid):
        '''
        :param uuid:
        :return: 图形验证码
        '''
        # 生成图形验证码
        text, image = captcha.generate_captcha()
        # 连接redis数据库
        redis_connections = get_redis_connection("verifications")
        # 保存图形验证码到数据库
        redis_connections.setex("image_%s" % uuid, 300, text)
        # 返回响应
        # content_type 为返回的类型是什么
        return HttpResponse(image, content_type="image/jpg")


# 短信验证码
class Sms_codeView(View):
    def get(self, request, mobile):
        # 先验证图形验证码是否输入正确
        image_code = request.GET.get("image_code")
        uuid = request.GET.get("uuid")
        if not all([image_code, uuid]):
            return HttpResponseForbidden(
                {"code": "0", "error_message": "请输入参数"})
        # 若存在 验证session里面的图形验证码是否一致
        redis_connections = get_redis_connection("verifications")
        # 验证是否已经发送给短信验证码
        send_flag = redis_connections.get("send_flag_%s" % mobile)
        if send_flag:
            return JsonResponse({"code": "0", "error_message": "短信验证码已经发送过了"})

        redis_image_code = redis_connections("image_%s" % uuid)
        # 比较图形验证码是否存在 是否已经过期
        if redis_image_code is None:
            return JsonResponse({"code": "0", "error_message": "图形验证码已经失效"})
        # 删除图形验证码 保证只使用一次
        redis_connections.delete("image_%s" % uuid)
        # 比较前端输入的图形验证码和redis里面的是否一样
        if image_code.lower() != redis_image_code.decode().lower():
            return HttpResponseForbidden(
                {"code": "0", "error_messaeg": "图形验证码输入有误"})
        # 此时验证通过 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        # 保存短信验证码
        # redis_connections.setex("sms_%s"% mobile,300,sms_code)
        # redis_connections.setex("send_flag_%s" % mobile,300,1)

        # 通过redis管道的方式
        # 创建管道
        p1 = redis_connections.pipeline()
        # 将命令添加到数据库
        p1.setex("sms_%s" % mobile, 300, sms_code)
        p1.setex("send_flag_%s" % mobile, 300, 1)
        # 执行此操作
        p1.execute()
        # 发送短信验证码
        # Send_sms.send_sms(1,mobile,(sms_code,5))
        send_sms_code.delay(mobile.sms_code)
        # 返回响应
        return JsonResponse({"code": "1", "error_message": "短信验证码发送成功"})
