from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal

from .models import OrderInfo
from goods.models import SKU


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        # order_id ：输出；address 和 pay_method : 输入
        read_only_fields = ('order_id',)
        # 指定address 和 pay_method 为输出
        extra_kwargs = {
            'address': {
                'write_only': True
            },
            'pay_method': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        # 获取当前保存订单时需要的信息
        user = self.context['request'].user
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        address = validated_data.get('address')
        pay_method = validated_data.get('pay_method')

        # 保存订单基本信息 OrderInfo(一)
        OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=1,
            total_amount=Decimal('0.00'),
            freight=Decimal('10.00'),
            pay_method=pay_method,
            status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM["UNSEND"]
        )


class CartSKUSerializer(serializers. ModelSerializer):
    """
    购物车商品数据序列化
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)
