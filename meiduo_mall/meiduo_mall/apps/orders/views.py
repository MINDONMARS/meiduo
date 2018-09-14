from django.shortcuts import render

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_redis import get_redis_connection
from decimal import Decimal
from rest_framework.response import Response

from goods.models import SKU
from . import serializers

# Create your views here.


class OrderView(CreateAPIView):
    """订单视图"""

    # 指定序列化器
    serializer_class = '序列化器'
    permission_classes = [IsAuthenticated]


class OrderSettlementView(APIView):
    """订单结算"""

    # 登录用户才能访问
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取"""

        user = request.user
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        redis_selected = redis_conn.smembers('selected_%s' % user.id)

        cart = {}
        for sku_id in redis_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        skus = SKU.objects.filter(id__in=cart.keys())

        for sku in skus:
            sku.count = cart[sku.id]

        freight = Decimal('10.00')

        order_data = {
            'freight': freight,
            'skus': skus
        }

        serializer = serializers.OrderSettlementSerializer(order_data)
        return Response(serializer.data)


