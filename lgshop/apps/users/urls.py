from django.urls import path,re_path
from . import views

app_name = "users"

urlpatterns = [
    path("register/",views.RegisterUser.as_view(),name="register"),
    re_path("username/(?P<username>[a-zA-Z0-9_-]{5,20})/count/",views.UsernameCount.as_view()),
    re_path("mobile/(?P<mobile>1[23456789]\d{9})/count/",views.MobileCount.as_view()),
    path("login/",views.LoginUserView.as_view(),name="login"),
    path("logout/",views.LoginoutView.as_view(),name="logout"),
    path("info/",views.InforView.as_view(),name="info"),
    path("emails/",views.EmailView.as_view(),name="email"),
    path("emails/verifications/",views.VerifyEmailView.as_view()),
]