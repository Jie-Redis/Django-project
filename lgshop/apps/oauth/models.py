from django.db import models
from users.models import Users
from utils.models import BaseModel


class QQauthUser(BaseModel):
    user = models.ForeignKey("users.Users", on_delete=models.CASCADE, verbose_name="用户")
    openid = models.CharField(max_length=100, verbose_name="openid")

    class Meta:
        db_table = "oauth_qq"
        verbose_name = "QQ登录用户"
        verbose_name_plural = verbose_name
