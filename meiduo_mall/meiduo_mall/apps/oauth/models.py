from django.db import models

from meiduo_mall.utils.models import BaseModel
# Create your models here.


class OAuthQQUser(BaseModel):
    """
    QQ登录用户数据：需要使用QQ账户绑定美多账户
    openid : 表示QQ账户
    user ：表示美多账户
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name
