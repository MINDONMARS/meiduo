# 定义耗时的异步任务
from celery_tasks.main import celery_app

from . import constants
from .yuntongxun.sms import CCP


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    定义发短信异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: None
    """
    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
