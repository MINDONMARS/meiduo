# from rest_framework import serializers
# from .utils import check_save_user_token
# from django_redis import get_redis_connection
# from users.models import User
# from .models import OAuthQQUser
#
#
# class QQAuthUserSerializer(serializers.Serializer):
#     """
#     QQ登录创建用户序列化器
#     """
#     access_token = serializers.CharField(label='操作凭证')
#     mobile = serializers.RegexField(label='手机号码', regex=r'^1[3-9]\d{9}$')
#     password = serializers.CharField(label='密码', max_length=20, min_length=8)
#     sms_code = serializers.CharField(label='短信验证码')
#
#     def validate(self, data):
#         # 检验accesss_token
#         access_token = data['access_token']
#         # 获取身份凭证
#         openid = check_save_user_token(access_token)
#         if not openid:
#             raise serializers.ValidationError('无效的openid')
#         data['openid'] = openid
#
#         # 校验短息验证码
#         mobile = data['mobile']
#         sms_code = data['sms_code']
#         redis_conn = get_redis_connection('verify_codes')
#         real_sms_code = redis_conn.get('sms_%s' % mobile)
#         if real_sms_code.decode() != sms_code:
#             raise serializers.ValidationError('手机验证码错误')
#
#         # 如果用户存在检查用户密码
#         try:
#             user = User.objects.get(mobile=mobile)
#         except User.DoesNotExist:
#             pass
#         else:
#             password = data['password']
#             if not user.check_password(password):
#                 raise serializers.ValidationError('密码错误')
#             data['user'] = user
#         return data
#
#
#     def create(self, validated_data):
#         user = validated_data.get('user')
#         if not user:
#             user = User.objects.create_user(
#                 username=validated_data['mobile'],
#                 mobile=validated_data['mobile'],
#                 password=validated_data['password']
#             )
#         # 绑定openid
#         OAuthQQUser.objects.create(openid=validated_data['openid'], user=user)
#         return user
#

import re
from rest_framework import serializers
from .utils import check_save_user_token
from django_redis import get_redis_connection
from users.models import User
from .models import OAuthQQUser


class QQAuthUserSerializer(serializers.Serializer):

    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', min_length=8, max_length=20)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):

        # 校验access_token 获取openid
        access_token = attrs['access_token']
        openid = check_save_user_token(access_token)
        if not openid:
            raise serializers.ValidationError('无效的access_token')
        attrs['openid'] = openid

        # 校验手机验证码
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if not user:
            user = User.objects.create_user(
                username=validated_data['mobile'],
                password=validated_data['password'],
                mobile=validated_data['mobile']
            )
        OAuthQQUser.objects.create(openid=validated_data['openid'], user=user)
        return user
