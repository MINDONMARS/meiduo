from django.shortcuts import render

from rest_framework.views import APIView

from . import serializers

# Create your views here.


# url(r'^carts/$', views.CartView.as_view()),
class CartView(APIView):
    """购物车增删改差"""

    def perform_authentication(self, request):
        """
        先延后认证(登录和没登录用户都要能进来)
        """
        pass

    def post(self, request):
        """添加购物车"""
        # 创建序列化器对象
        serializer = serializers.CartSerializer(data=request.data)
        # 校验
        serializer.is_valid(raise_exception=True)

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 已登录 操作redis
            pass
        else:
            # 未登录 操作cookie
            pass

    def get(self, request):
        """查询购物车"""
        pass

    def put(self, request):
        """更新购物车"""
        pass

    def delete(self, request):
        """删除购物车"""
        pass
