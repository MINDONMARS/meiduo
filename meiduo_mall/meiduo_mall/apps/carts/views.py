from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import status
import base64, pickle

from . import serializers
from goods.models import SKU

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

        # 读取校验后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 已登录 操作redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()

            # 给redis购物车做增量存储,计算
            # redis_conn.hincrby(name, key, amount=1)
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 未登录 操作cookie
            # 获取浏览器中的cookie数据
            cart_str = request.COOKIES.get('cart')

            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)

            else:
                cart_dict = {}  # 保证用户即使是第一次使用cookie保存购物车数据，也有字典对象可以操作
            if sku_id in cart_dict:
                # 要添加的商品购物车里已经有了, 累加
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 编个码丢出去
            cookie_cart_dict_bytes = pickle.dumps(cart_dict)
            cookie_cart_str_bytes = base64.b64encode(cookie_cart_dict_bytes)
            cookie_cart_str = cookie_cart_str_bytes.decode()
            # 写入cookie
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cookie_cart_str)
            return response

    def get(self, request):
        """查询购物车"""
        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            # 已登录, 读redis
            redis_conn = get_redis_connection('cart')
            # 查询redis中的购物车数据:
            # 注意点：python3中的从redis读取的数据都是bytes类型的数据
            # redis_cart_dict = {b'sku_id_1': b'count_1', b'sku_id_2': b'count_2'}
            redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
            # 查询是否勾选
            # redis_selected = [b'sku_id_1']
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            cart_dict = {}
            for sku_id, count in redis_cart_dict.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected  # 如果sku_id在redis_selected中，返回True;反之，返回False
                }

        else:
            # 没有登录
            cart_str = request.COOKIES.get('cart')

            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

        # 序列化响应 其中count, selected字段没有自己加
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:

            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']  # 给商品对象加了两个序列化用的字段
        serializer = serializers.GetCartSerializer(skus, many=True)

        return Response(serializer.data)

    def put(self, request):
        """更新购物车"""
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 读取校验后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        # 用户登录
        if user is not None and user.is_authenticated:
            # 修改redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()

            pl.hset('cart_%s' % user.id, sku_id, count)

            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)

        else:
            # 修改cookie

            # 获取cookie
            cart_str = request.COOKIES.get('cart')

            # 如果有
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)
            # 如果没有
            else:
                cart_dict = {}
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 编码丢出去
            cart_dict_bytes = pickle.dumps(cart_dict)
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            cart_str = cart_str_bytes.decode()

            response = Response(serializer.data)
            response.set_cookie('cart', cart_str)
            return response

    def delete(self, request):
        """删除购物车"""
        serializer = serializers.DelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data.get('sku_id')

        # 用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        # 用户已登录
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')

            redis_conn.hdel('cart_%s' % user.id, sku_id)
            redis_conn.srem('selected_%s' % user.id, sku_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            # 获取cookie
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)

            else:
                cart_dict = {}

            sku_ids = cart_dict.keys()
            response = Response(status=status.HTTP_204_NO_CONTENT)
            if sku_id in sku_ids:
                cart_dict.pop(sku_id)

                cookie_dict_bytes = pickle.dumps(cart_dict)
                cookie_str_bytes = base64.b64encode(cookie_dict_bytes)
                cookie_str = cookie_str_bytes.decode()

                response.set_cookie('cart', cookie_str)
            return response




class SelectAll(APIView):
    """全选"""

    def perform_authentication(self, request):

        pass

    def put(self, request):
        serializer = serializers.SelectAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        # 如果user已登录 更新redis
        if user is not None and user.is_authenticated:
            # 创建redis对象
            redis_conn = get_redis_connection('cart')
            # 获取selected
            pl = redis_conn.pipeline()
            cart = redis_conn.hgetall('cart_%s' % user.id)
            sku_ids = cart.keys()
            if sku_ids:
                if selected:
                    pl.sadd('selected_%s' % user.id, *sku_ids)
                else:
                    pl.srem('selected_%s' % user.id, *sku_ids)
                pl.execute()
            return Response(serializer.data)

        # 用户未登录操作cookie
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)
                # 拿selected

                for sku_id in cart_dict:

                    cart_dict[sku_id]['selected'] = selected

                cookie_cart_dict_bytes = pickle.dumps(cart_dict)
                cookie_cart_str_bytes = base64.b64encode(cookie_cart_dict_bytes)
                cookie_cart_str = cookie_cart_str_bytes.decode()

                response = Response(serializer.data)
                response.set_cookie('cart', cookie_cart_str)
                return response
            return Response({'message': 'ok'})