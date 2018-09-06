from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from .models import User
from .serializers import CreateUserSerializer, UserDetialSerializer, EmailSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class EmailView(UpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetialView(RetrieveAPIView):
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