import base64, pickle
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """购物车合并工具方法"""

    # 读取cookie
    cart_str = request.COOKIES.get('cart')
    # 如果没有直接返回
    if not cart_str:
        return response

    # 转化为cookie字典对象
    cart_str_bytes = cart_str.encode()
    cart_dict_bytes = base64.b64decode(cart_str_bytes)
    # {sku_id:{count:xxx, selected:xxx}}
    cart_dict = pickle.loads(cart_dict_bytes)

    # 读取redis
    redis_conn = get_redis_connection('cart')

    # hash里的 cart_userid: {sku_id: count}
    redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
    # set里的('selected_userid')
    redis_cart_selected = redis_conn.smembers('selected_%s' % user.id)
    for sku_id, cookie_dict in cart_dict.items():
        # redis_cart_dict
        redis_cart_dict[sku_id] = cookie_dict['count']
        # redis_cart_selected
        if cookie_dict['selected']:
            redis_cart_selected.add(sku_id)
    # 合并完推进redis
    pl = redis_conn.pipeline()
    pl.hmset('cart_%s' % user.id, redis_cart_dict)
    pl.sadd('selected_%s' % user.id, *redis_cart_selected)
    pl.execute()
    # 完事清空cookie
    response.delete_cookie('cart')
    return response