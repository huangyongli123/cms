import random

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.yuntongxun.sms import CCP


class SmsCodeView(APIView):
    def get(self,request,mobile):
        # """获取短信验证码接口"""

        strict_redis = get_redis_connection('verify_codes')

    # 4.校验是否重复发送

        sms_flag = strict_redis.get('sms_flag_%s' % mobile)


        if sms_flag:
            return Response({'message': '短信发送过于频繁'}, status=400)
    #1.生成短信验证码
        sms_code='%06d'%random.randint(0,999999)
        print(sms_code)
    #2.发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
    #3.保存短信验证码


        #设置短信验证码有效期为5分钟
        real_code=strict_redis.setex('sms_%s'%mobile,60*5,sms_code)
        print(real_code)

        #设置60秒内不能重复发送
        strict_redis.setex('sms_flag_%s'%mobile,60,1)




        #5.响应数据
        return Response({'message':'短信发送成功'})
