from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import User
from .serializers import CreateUserSerializer, UserDetialSerializer, EmailSerializer

# Create your views here.


class VerifyEmailView(APIView):
    """实现邮箱的先验证激活"""

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)
        # 解token(去别地方)
        user = User.check_email_verify_url(token)
        if not user:
            return Response({'message': '无效token'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        return Response({'message': 'ok'})


class EmailView(UpdateAPIView):
    """天机邮箱"""

    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetialView(RetrieveAPIView):
    """用户基本信息"""

    serializer_class = UserDetialSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = CreateUserSerializer


class MobileCountView(APIView):
    """验证手机号是否重复"""
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


class UsernameCountView(APIView):
    """验证用户名是否存在"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)