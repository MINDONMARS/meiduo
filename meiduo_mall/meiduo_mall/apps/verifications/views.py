from django.shortcuts import render
from rest_framework.views import APIView
import random, logging
from django_redis import get_redis_connection
from . import constants
from meiduo_mall.libs.yuntongxun.sms import CCP
from rest_framework.response import Response
# Create your views here.


logger = logging.getLogger('django')


class SMSCodeView(APIView):
    """发送短信验证码"""

    def get(self, request, mobile):
        """
        GET /sms_code/(?<mobile>1[3-9]\d{9})/
        """
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)
        # 存到redis
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        return Response({'message': 'ok'})

