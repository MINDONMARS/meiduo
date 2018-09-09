from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import mixins

from users import constants
from .models import User, Address
from .serializers import CreateUserSerializer, UserDetialSerializer, EmailSerializer, AddressSerializer, AddressTitleSerializer

# Create your views here.


class AddressViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """收货地址增删改查"""

    # 指定序列化器/查询集
    serializer_class = AddressSerializer
    # queryset = Address.objects.all()

    # 增
    def create(self, request, *args, **kwargs):

        count = self.request.user.addresses.count()
        if count > 20:
            return Response({'message': '地址数量超出限制'}, status.HTTP_400_BAD_REQUEST)
        return super(AddressViewset, self).create(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'ok'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk):
        address = self.get_object()
        serializer = AddressTitleSerializer(address, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk):
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    """添加邮箱"""

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