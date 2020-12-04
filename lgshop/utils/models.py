from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="登录更新时间")

    class Meta:
        #数据库映射的时候 不会被创建
        abstract = True