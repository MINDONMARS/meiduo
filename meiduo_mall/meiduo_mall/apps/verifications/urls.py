from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^sms_codes/(?P<mobile>1[3-9][0-9]{9})/$', views.SMSCodeView.as_view())
]
