from django.forms import Form
from django import forms
from .models import Users

#表单验证
class UserForm(forms.Form):
    #验证参数
    username = forms.CharField(max_length=20,min_length=5,error_messages={"max_length":"用户名长度不对","min_length":"用户名长度不对"})
    password = forms.CharField(max_length=20,min_length=8,error_messages={"max_length":"密码长度不对","min_length":"密码长度不对"})
    password2 = forms.CharField(max_length=20,min_length=8,error_messages={"max_length":"密码长度不对","min_length":"密码长度不对"})
    mobile = forms.CharField(max_length=11,min_length=11,error_messages={"max_length":"手机号码长度不对","min_length":"手机号码长度不对"})
    sms_code = forms.CharField(max_length=6,min_length=6,required=True)
    #验证用户名是否已经存在
    def clean_username(self):
        username = self.cleaned_data.get("username")
        username_exist = Users.objects.filter(username=username).exist()
        if username_exist:
            raise forms.ValidationError("用户名已经存在")
        return username
    #验证两次密码是否一致
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password != password2 :
            raise forms.ValidationError("两次密码不一致")
    #验证手机号是否已经存在
    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        mobile_exist = Users.objects.filter(mobile=mobile).exist()
        if mobile_exist:
            raise forms.ValidationError("手机号已经存在")

#用户登录的表单验证
class LoginUserForm(forms.Form):
    username = forms.CharField(max_length=20,min_length=5)
    password = forms.CharField(max_length=20,min_length=8)
