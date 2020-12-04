from django.shortcuts import render,redirect,reverse
from django.views import View
from . import views
from django.http import HttpResponse,JsonResponse,HttpResponseForbidden,HttpResponseServerError
from .models import Users
from .forms import UserForm,LoginUserForm
from django_redis import get_redis_connection
from django.contrib.auth import login,authenticate,logout
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
import json,re
from celery_task.email.tasks import send_email
from .utils import generate_token,check_token


#用户的收货地址
class AddressView(LoginRequiredMixin,View):
    def get(self,request):
        #查询用户的收货地址
        pass


#用户中心
class InforView(LoginRequiredMixin,View):
    def get(self,request):
        context = {"username":request.user.username,
                   "mobile":request.user.mobile,
                   "email":request.user.email,
                   "email_active":request.user.email_active}
        return render(request,"user_center_info.html",context=context)

#添加邮箱
class EmailView(LoginRequiredMixin,View):
    def put(self,request):
        '''添加邮箱'''
        #接收参数
        email = json.loads(request.body.decode()).get("email")
        #校验参数
        if not re.match(r"^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$",email):
            return HttpResponseForbidden("邮箱输入有误")
        #将邮箱保存到数据库
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            return HttpResponseServerError("邮箱添加失败，请重新保存邮箱")
        #生成verify_url
        verify_url = generate_token(request.user)
        #发送邮件
        #此处使用celery异步的方式
        send_email.delay(email,verify_url)
        return JsonResponse({"code":"1","error_message":"邮件发送成功"})


#邮箱验证
class VerifyEmailView(View):
    def get(self,request):
        #接收参数
        token = request.GET.get("token")
        if not token:
            return HttpResponseForbidden("没有获得token")
        #进行去序列化
        user = check_token(token)
        if not user:
            return HttpResponseServerError("无效的token")
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            return HttpResponseServerError("邮箱激活失败")
        #返回响应
        return redirect(reverse("users:info"))



#用户登录
class LoginUserView(View):
    def get(self,request):
        '''提供用户登录的界面'''
        return render(request,"login.html")
    def post(self,request):
        '''验证用户登录'''
        #接收参数
        login_forms = LoginUserForm(request.POST)
        if login_forms.is_valid():
            username = login_forms.cleaned_data("username")
            password = login_forms.cleaned_data("password")
            remembered = request.POST.get("remembered")
        #校验参数
        # users = Users.objects.get(username=username).count()
        # if users == 0:
        #     return render(request,"login.html",{"username_errmsg":"该用户不存在，请先注册"})
        user = authenticate(username=username,password=password)
        if user is None:
            return render(request,"login.html",{"errmsg":"用户名或者密码输入错误"})
        #状态保持
        login(request,user)
        if remembered != "on":
            #页面关闭自动删除
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(3600*24*14)
        next = request.GET.get("next")
        if next:
            response = redirect(reverse(next))
        else:
            response = redirect(reverse("contents:index"))
        response.set_cookie("username",user.username,max_age=3600*24*14)
        return response


#退出登录
class LoginoutView(View):
    def get(self,request):
        #退出状态保持
        logout(request)
        response = redirect(reverse("contents:index"))
        response.delete_cookie("username")
        return response


#用户注册的视图函数
class RegisterUser(View):
    def get(self,request):
        #获取注册页面
        return render(request,"register.html")
    def post(self,request):
        #验证通过
        form = UserForm(request.POST)
        if form.is_valid():
            #接收参数
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            mobile = form.cleaned_data.get("mobile")
            sms_code = form.cleaned_data.get("sms_code")
            #验证短信验证码是否输入正确
            #连接redis
            redis_conn = get_redis_connection("verifications")
            #提取短信验证码
            redis_sms_code = redis_conn("sms_%s"% mobile)
            #验证是否一样
            #先验证是否存在该验证码
            if redis_sms_code is None:
                return JsonResponse({"code":"0","error_message":"该验证码已经失效"})
            #验证是否一样
            if sms_code != redis_sms_code:
                return JsonResponse({"code":"0","error_message":"短信验证码输入有误"})
            #保存数据到数据库
            #此时要做一个异常处理
            try:
                users = Users.objects.create_user(username=username,password=password,mobile=mobile)
            except:
                return render(request,"register.html",{"error_message":"注册失败请重新注册"})
            #用户状态保持
            login(request,users)
            #注册成功 重定向到首页
            return redirect(reverse("content:index"))


#验证用户名是否已经存在视图
class UsernameCount(View):
    def get(self,request,username):
        count = Users.objects.filter(username=username).count()
        return JsonResponse(count)


#验证手机号码是否已经存在
class MobileCount(View):
    def get(self,request,mobile):
        count =Users.objects.filter(mobile=mobile).count()
        return JsonResponse(count)