from django.shortcuts import render

from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Area
from . import serializers

# Create your views here.


class AreasViewset(ReadOnlyModelViewSet):
    """省市区三级联动数据"""

    pagination_class = None

    # 根据行为指定查询集
    def get_queryset(self):
        if self.action == 'list':
            queryset = Area.objects.filter(parent=None)
        else:
            queryset = Area.objects.all()
        return queryset

    # 指定序列化器
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer

