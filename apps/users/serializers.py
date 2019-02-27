import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import User, Area


class UserRegisterSerializer(ModelSerializer):
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    password2 = serializers.CharField(label="确认密码", write_only=True)
    allow = serializers.BooleanField(label="确认是否勾选", write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'sms_code', 'password2', 'mobile', 'allow','token')
        extra_kwargs = {
            'username': {

                'min_length': 5,
                'max_length': 20,
                'error_messages': {#error_messages
                    'min_length': '只允许5-20个字符的用户名',
                    'max_length': '只允许5-20个字符的用户名'
                }
            },
            'password': {
                'write_only': True,
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '只允许5-20个字符的密码',
                    'max_length': '只允许5-20个字符的密码'
                }
            }
        }

    def create(self, validated_data):
        """添加一条用户数据"""


        user = User.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            mobile=validated_data.get('mobile'),
        )
        # 注册成功自动登陆
        # todo: 生成jwt字符串
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生payload部分的方法(函数)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt的方法(函数)
        #  {'exp': xxx, 'email': '', 'user_id': 1, 'username': 'admin'}
        # user：登录的用户对象
        payload = jwt_payload_handler(user)  # 生成payload, 得到字典
        token = jwt_encode_handler(payload)  # 生成jwt字符串

        # 给user对象新增一个token的属性
        user.token = token


        return user

    def validate_mobile(self, value):
        """校验手机号输入格式是否正确"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式输入错误')
        return value

    def validate_allow(self, value):
        """校验是否勾选用户协议"""
        if not value:
            raise serializers.ValidationError('请勾选用户协议')
        return value



    def validate(self, attrs):
        """校验密码和短信验证码"""
        # 1.校验两次输入的密码是否正确
        password = attrs['password']
        password2 = attrs['password2']
        if password2 != password:
            raise serializers.ValidationError('两次密码输入不一致')
        # 2.校验短信验证码是否正确
        mobile = attrs['mobile']
        strict_redis = get_redis_connection('verify_codes')
        real_sms_code = strict_redis.get('sms_%s' % mobile)

        if not real_sms_code:
            raise serializers.ValidationError('短信验证码不存在')
        if real_sms_code.decode() != attrs['sms_code']:
            raise serializers.ValidationError('短信验证码输入错误')
        return attrs


# areas/serializers.py
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializer(serializers.ModelSerializer):
    """ 子行政区划信息序列化器 """
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')  # Area模型类中中 related_name 的值