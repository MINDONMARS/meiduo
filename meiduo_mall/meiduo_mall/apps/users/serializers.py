import re
from django_redis import get_redis_connection

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import User


class EmailSerializer(serializers.ModelSerializer):
    """添加邮箱序列化器"""
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()

        return instance


class UserDetialSerializer(serializers.ModelSerializer):
    """对用户基本信息进行序列化"""

    class Meta:
        model = User
        fields = ('username', 'mobile', 'email', 'email_active')


class CreateUserSerializer(serializers.ModelSerializer):
    # 定义外部字段
    password2 = serializers.CharField(label='确认密码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    # 加入token字段
    token = serializers.CharField(label='登录状态token', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'password', 'password2', 'allow', 'sms_code', 'token']

        extra_kwarg = {
            'username': {
                'min_length': 5,
                'max_lenght': 20,
                'error_messages': {
                    'min_length': '仅允许5到20个字符的用户名',
                    'max_length': '仅允许5到20个字符的用户名'
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_lenght': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码'
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号码格式错误')
        return value

    def validate_allow(self, value):
        """验证是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):

        # 校验密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')
        # 校验短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')
        return data

    def create(self, validated_data):
        """
        重写序列化器的create方法, password2, allow, sms_code不能存
        :param validated_data: 验证后的数据
        :return: user模型对象
        """
        validated_data.pop('password2')
        validated_data.pop('allow')
        validated_data.pop('sms_code')

        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # 必须在注册或者登录之后，响应注册或者登录结果之前，生成jwt_token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 生成载荷：包含了user_id,username,email
        payload = jwt_payload_handler(user)
        # jwt_token
        token = jwt_encode_handler(payload)
        # 将token添加到user : python是面向对象的高级动态编程语言
        user.token = token

        # 响应数据:只会响应read_only字段,
        # 输出字段(read_only)：'id', 'username', 'mobile', 'token'

        return user
