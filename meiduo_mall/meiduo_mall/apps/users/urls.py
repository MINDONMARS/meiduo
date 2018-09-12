from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

urlpatterns = [

    # 判断用户名是否重复
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 注册
    url(r'^users/$', views.UserView.as_view()),

    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^user/$', views.UserDetialView.as_view()),
    url(r'^email/$', views.EmailView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # 用户浏览记录
    url(r'^browse_histories/$', views.UserBrowsingHistoryView.as_view()),
]

router = DefaultRouter()
router.register('addresses', views.AddressViewset, base_name='addresses')
urlpatterns += router.urls

