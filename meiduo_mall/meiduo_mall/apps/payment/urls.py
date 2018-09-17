from django.conf.urls import url

from . import views

urlpatterns = [
    # 支付订单
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
    # 获取支付结果
    url(r'^payment/status/$', views.PaymentStatusView.as_view()),
]