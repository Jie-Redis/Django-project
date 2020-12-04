from django.db import models


#省市区
class AccessModel(models.Model):
    name = models.CharField(max_length=20,verbose_name="名称")
    parent = models.ForeignKey("self",on_delete=models.SET_NULL,null=True,blank=True,verbose_name="上级行政区",related_name="subs")


    class Meta:
        db_table = "tb_areas"
        verbose_name = "省市区"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
