from django.urls import path,re_path
from django import views
from . import views

urlpatterns = [
    re_path("image_codes/(?P<uuid>[\w-]+)/",views.ImageCodeView.as_view()),
    re_path("sms_codes/(?P<mobile>1[2-9]\d{9})/",views.Sms_codeView.as_view()),
]