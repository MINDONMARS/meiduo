from django.conf.urls import url
from . import views

urlpatterns = [
    url('^orders/settlement/$', views.OrderSettlementView.as_view()),
    url('^orders/$', views.OrderView.as_view())
]
