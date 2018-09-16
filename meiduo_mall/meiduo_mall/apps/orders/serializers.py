from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from django_redis import get_redis_connection
from django.db import transaction

from .models import OrderInfo, OrderGoods
from goods.models import SKU
import time


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

        # 从第一次操作数据库开始, 明显开启一次事务
        with transaction.atomic():

            # 在操作数据之前创建一个保存点, 表示回滚/提交到此
            save_id = transaction.savepoint()
            # 防止其他错误(服务器挂了)暴力回滚整体try
            try:
                # 保存订单基本信息 OrderInfo(一)
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM["UNSEND"]
                )

                # 查出订单商品信息, 构建新数据, 然后sku表减库存, 加销量 goods表加销量

                # 创建链接redis对象
                redis_conn = get_redis_connection('cart')
                # 拿出购物车所有数据
                redis_cart = redis_conn.hgetall('cart_%s' % user.id)
                redis_selected = redis_conn.smembers('selected_%s' % user.id)

                # 构建购物车中已勾选的新数据
                carts = {}
                for sku_id in redis_selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])

                # 获取购物车已勾选的所有sku对象
                sku_ids = carts.keys()
                for sku_id in sku_ids:
                    while True:
                        sku = SKU.objects.get(id=sku_id)

                        # 获取原始库存/销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 当前购买数量
                        cart_sku_count = carts.get(sku_id)

                        # 判断库存是否充足
                        if cart_sku_count > origin_stock:
                            # 出错就回滚到保存点
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError('库存不足')
                        time.sleep(10)

                        # sku减库存加销量
                        new_stock = origin_stock - cart_sku_count
                        new_sales = origin_sales + cart_sku_count

                        # 同步到数据库
                        # 更新之前先使用原始数据查询该商品记录在不在, 如果在就更新, 不在会返回0
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock, sales=origin_sales).update(stock=new_stock, sales=new_sales)
                        if result == 0:
                            # 不能直接抛出异常, 要让返回循环让用户再进行上面的库存判断,在数据成功保存/抛出库存不足后异常后跳出循环
                            continue

                        # 获取spu对象, 修改spu销量
                        sku.goods.sales += cart_sku_count
                        # 同步到数据库
                        sku.goods.save()

                        # 提交的订单中的商品表添加数据
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=cart_sku_count,
                            price=sku.price
                        )
                        # 修改订单默认计数
                        order.total_count += cart_sku_count
                        # 修改默认总价
                        order.total_amount += (cart_sku_count * sku.price)
                        # 跳出循环
                        break

                    # 最后给总价加上运费
                    order.total_amount += order.freight
                    # 同步到数据库
                    order.save()
                # 捕获try出来的异常
            except serializers.ValidationError:
                raise
            except Exception:

                transaction.savepoint_rollback(save_id)
                raise

            # 执行成功 提交事务到保存点
            transaction.savepoint_commit(save_id)

        # 清空购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('cart_%s' % user.id, *redis_selected)
        pl.srem('selected_%s' % user.id, *redis_selected)
        pl.execute()

        return order


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
