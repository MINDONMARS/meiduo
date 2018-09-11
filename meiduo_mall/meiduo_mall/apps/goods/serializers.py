from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer

from .models import GoodsCategory, GoodsChannel, SKU
from goods.search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'comments', 'default_image_url']


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')


class CategorySerializer(serializers.ModelSerializer):
    """
    类别序列化器
    """
    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')


class ChannelSerializer(serializers.ModelSerializer):
    """
    频道序列化器
    """
    category = CategorySerializer()

    class Meta:
        model = GoodsChannel
        fields = ('category', 'url')


