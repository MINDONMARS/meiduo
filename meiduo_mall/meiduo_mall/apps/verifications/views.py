import logging
import random

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from celery_tasks.sms.tasks import send_sms_code
from . import constants

logger = logging.getLogger('django')


class SMSCodeView(APIView):
    """发送短信验证码"""

    def get(self, request, mobile):
        """
        GET /sms_code/(?<mobile>1[3-9]\d{9})/
        """
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({'message': '请勿频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)
        # 存到redis
        # redis管道:将多个redis指令放在一个管道里面，统一执行，减少redis数据库访问的频率，提升性能
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 添加redis标记校验用户60秒内是否重复发送
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 完了要执行一下管道
        pl.execute()
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        send_sms_code.delay(mobile, sms_code)  # 调用delay(),触发celery异步任务
        return Response({'message': 'ok'})

