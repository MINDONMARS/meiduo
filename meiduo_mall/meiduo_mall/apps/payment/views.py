from django.shortcuts import render
from alipay import AliPay
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import status
from django.conf import settings
import os

from orders.models import OrderInfo
from .models import Payment

# Create your views here.


class PaymentView(APIView):
    """支付宝支付"""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单不存在'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建链接支付宝对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 调用支付宝方法
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='美多商城%s' % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string
        # 响应alipay_url
        return Response({
            'alipay_url': alipay_url
        })