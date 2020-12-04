from django.shortcuts import render, redirect, reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import QQauthUser
from django.contrib.auth import login
from .utils import generate_openid, check_openid
from django_redis import get_redis_connection
from users.models import Users


# QQ扫码的界面
class QQoauthView(View):
    '''qq登录的页面'''

    def get(self, request):
        # 接收next
        next = request.GET.get("next")
        # 创建auth对象
        oauth = OAuthQQ(settings.QQ_CLIENT_ID, settings.QQ_CLIENT_SECRET,
                        settings.QQ_REDIRECT_URI)
        # 获取qq登录的扫码链接地址url
        login_url = oauth.get_qq_url()
        return JsonResponse(
            {"code": "1", "error_message": "", "login_url": login_url})


# QQ登录后的回调界面
class QQAuthUserView(View):
    def get(self, request):
        '''获取qq登陆后的回调界面'''
        # 获取code
        code = request.GET.get("code")
        if not code:
            return HttpResponse("获取code失败")
        # 创建oauth对象
        oauth = OAuthQQ(settings.QQ_CLIENT_ID, settings.QQ_CLIENT_SECRET,
                        settings.QQ_REDIRECT_URI)
        # 获取access_token
        try:
            access_token = oauth.get_access_token(code)
            # 获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            return HttpResponse("openid获取失败")
        # 查询数据库是否已经绑定
        try:
            oauth_user = QQauthUser.objects.get(openid=openid)
        except Exception as e:
            # 没有查询到 返回一个绑定的界面
            # 对openid进行一个加密处理
            openid = generate_openid(openid)
            # 传入到前端
            context = {"access_token_openid": openid}
            return render(request, "oauth_callback.html",
                          {"error_message": "该用户未绑定"}, context=context)
        else:
            # 已经绑定
            # 状态保持
            login(request, oauth_user.user)
            # 返回到页面
            next = request.GET.get("state")
            if next != "None":
                response = redirect(reverse(next))
            else:
                response = redirect(reverse("contents:index"))
            # 显示用户名
            response.set_cookie("username", oauth_user.user.username,
                                max_age=3600 * 24 * 14)
            # 返回响应
            return response

    def post(self, request):
        # 未绑定的用户 绑定
        # 接收数据
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        sms_code = request.POST.get("sms_code")
        access_token_openid = request.POST.get("access_token_openid")
        # 校验参数
        # 校验sms_code
        redis_connection = get_redis_connection("verifications")
        sms_code_redis = redis_connection.get("sms_%s" % mobile)
        if sms_code_redis is None:
            return render(request, "oauth_callback.html",
                          {"error_message": "短信验证码已经失效了"})
        if sms_code != sms_code_redis:
            return render(request, "oauth_callback.html",
                          {"error_message": "短信验证码输入错误"})
        # 判断openid是否存在
        openid = check_openid(access_token_openid)
        if openid is None:
            return render(request, "oauth_callback.html",
                          {"error_message": "openid已经失效"})
        # 查询用户是否已经存在
        try:
            user = Users.objects.get(mobile=mobile)
        except Exception as e:
            # 如果没有这个对象 就创建一个对象
            user = Users.objects.create_user(mobile=mobile, username=mobile,
                                             password=password)
        else:
            # 用户存在就检查密码是否正确
            if not user.check_password(password):
                return render(request, "oauth_callback.html",
                              {"error_message": "密码与原密码不一致"})
        # 已经存在这个对象 就进行openid和user绑定
        try:
            QQauth_user = QQauthUser.objects.create(openid=openid, user=user)
        except Exception as e:
            return render(request, "oauth_callback.html",
                          {"error_message": "密码输入错误"})
        else:
            # 状态保持
            login(request, user)
            # 跳转到之前界面
            next = request.GET.get("state")
            if next != "None":
                response = redirect(reverse(next))
            else:
                response = redirect(reverse("contents:index"))
            # 用户名显示
            response.set_cookie("username", user.username,
                                max_age=3600 * 24 * 14)
            # 返回响应
            return response
