from django.shortcuts import render

from rest_framework.views import APIView

# Create your views here.


# url(r'^carts/$', views.CartView.as_view()),
class CartView(APIView):
    """购物车增删改差"""

    def post(self, request):
        """添加购物车"""
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
