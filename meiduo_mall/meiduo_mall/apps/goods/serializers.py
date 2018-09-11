from rest_framework import serializers

from .models import GoodsCategory, GoodsChannel, SKU


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'comments', 'default_image_url']



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