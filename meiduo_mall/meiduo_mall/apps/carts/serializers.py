from rest_framework import serializers

from goods.models import SKU


class SelectAllSerializer(serializers.Serializer):
    selected = serializers.BooleanField(label='是否全选')


class GetCartSerializer(serializers.ModelSerializer):
    """获取购物车序列化器"""
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')



class CartSerializer(serializers.Serializer):
    """购物车序列化器"""
    sku_id = serializers.IntegerField(label='商品ID', min_value=1)
    count = serializers.IntegerField(label='商品质量', min_value=1)
    selected = serializers.BooleanField(default=True, label='是否勾选')

    def validate_sku_id(self, value):
        """校验sku_id, 判断是否存在"""
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id不存在')

        return value
