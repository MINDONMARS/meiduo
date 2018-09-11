from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from .models import SKU, GoodsCategory
from .serializers import ChannelSerializer, CategorySerializer, SKUSerializer


# Create your views here.


class SKUListView(ListAPIView):
    """商品列表:排序和分页"""
    # 指定序列化器
    serializer_class = SKUSerializer
    # 指定排序后端
    filter_backends = [OrderingFilter]
    # 指定排序字段
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        # 必须是上架商品
        return SKU.objects.filter(category_id=category_id, is_launched=True)


# url(r'^categories/(?P<pk>\d+)/$', views.CategoryView.as_view()),
class CategoryView(GenericAPIView):
    """
    商品列表页面包屑导航
    """
    queryset = GoodsCategory.objects.all()

    def get(self, request, pk=None):
        ret = dict(
            cat1='',
            cat2='',
            cat3=''
        )
        category = self.get_object()
        if category.parent is None:
            # 当前类别为一级类别
            ret['cat1'] = ChannelSerializer(category.goodschannel_set.all()[0]).data
        elif category.goodscategory_set.count() == 0:
            # 当前类别为三级
            ret['cat3'] = CategorySerializer(category).data
            cat2 = category.parent
            ret['cat2'] = CategorySerializer(cat2).data
            ret['cat1'] = ChannelSerializer(cat2.parent.goodschannel_set.all()[0]).data
        else:
            # 当前类别为二级
            ret['cat2'] = CategorySerializer(category).data
            ret['cat1'] = ChannelSerializer(category.parent.goodschannel_set.all()[0]).data

        return Response(ret)
