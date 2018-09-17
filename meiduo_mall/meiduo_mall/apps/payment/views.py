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


class PaymentStatusView(APIView):
    """
    1.支付宝流水号绑定美多order_id
    2.修改订单状态(UNPAID-->UNSEND)
    """

    def put(self, request):
        """
        读取查询字符串中支付宝重定向的参数
        out_trade_no=20180917012326000000001 (美多商城维护订单编号)
        sign：sign=q722wKrDJvRWrNNs5gwmLuKFW（验证本次通知、重定向是否来源自支付宝）
        trade_no：trade_no=2018091721001004510500275863（支付宝生成的交易流水号）
        """
        # data = ?charset=utf-8&out_trade_no=20180917012326000000001&method=alipay.trade.page.pay.return&total_amount=3798.00&sign=q722wKrDJvRWrNNs5gwmLuKFWNLhyfzqisWFAhQ4aqK6RuUpo73%2BZzSO5hwdglPlapGHYhR0ZpsB%2FlAH8SyAG6sU49VkvM3Juyhlr1d8eL62N5NCy6q1rCd2PN%2FRbK4xouzrbIxESBruFVBFabWaAcAH5iOB2yknvST9x5wWd09jIHtoIZ515nZC98ud0v298kYWe%2FY63iMVOkrVC55Lx0ebgU%2FsmnWv3DFIgeW6UiEno%2BwjeezYn6u8XCqJGrCkBXLBr9X3tk%2BN%2FwbgankTYJvLtwMkc4nZsWrPIt7eXI3wtq4u341gEkgaEoNDMgtC0CaTD9PDNVT89ASiayvFqw%3D%3D&trade_no=2018091721001004510500275863&auth_app_id=2016082100308405&version=1.0&app_id=2016082100308405&sign_type=RSA2&seller_id=2088102172481561&timestamp=2018-09-17+09%3A52%3A40

        # 支付宝流水号绑定美多order_id
        data = request.query_params.dict()
        # 从查询字符串中弹出'sign', 并接收
        signature = data.pop('sign')

        # 创建SDK Alipay对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url

            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,

            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        success = alipay.verify(data, signature)

        if success:
            # 认证成功
            # 读取order_id和trade_id
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')

            # 绑定在一个新表
            Payment.objects.create(order_id=order_id, trade_id=trade_id)

            # 修改order.status
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"]).update(status=OrderInfo.ORDER_STATUS_ENUM["UNSEND"])
            return Response({'trade_id': trade_id})
        else:
            # 认证失败
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)


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