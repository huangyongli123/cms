from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.cart import serializers
from apps.cart.serializers import CartAddSerializer
from apps.goods.models import Goods


class CartView(APIView):
    def post(self, request):
        """添加购物车"""
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        goods_id = serializer.validated_data.get('goods_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        # 获取用户
        user = request.user

        if user.is_authenticated():   # 判断是否已登录
            # 用户已登录，获取操作Redis的StrictRedis对象
            redis = get_redis_connection('cart')
            # 增加购物车商品数量
            redis.hincrby('cart_%s' % user.id, goods_id, count)
            # 保存商品勾选状态
            if selected:
                redis.sadd('carts_selected_%s' % user.id, sku_id)
            # 响应序列化数据
                return Response(serializer.data, status=201)

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # 连接redis数据库
            redis = get_redis_connection('cart')  # type:StrictRedis
            # 获取商品及其数量
            # cart_1 = {1: 2, 2: 2}  商品数量存储
            dict_cart = redis.hgetall('carts_%s' % user.id)
            # 获取商品勾选状态
            # cart_selected_1 = {1,  2}  商品勾选状态
            list_cart = redis.smembers('carts_selected_%s' % user.id)
            # 拼装字典
            # {1:{'count':2, 'selected':False}, 2:{'count':2, 'selected':False}}
            cart = {}
            for goods_id, count in dict_cart.items():
                cart[int(goods_id)] = {
                    'count': int(count),
                    'selected': goods_id in list_cart
                }
            goods = Goods.objects.filter(id__in=cart.keys())
            for good in goods:
                good.count = cart[good.id]['count']
                good.selected = cart[good.id]['selected']
            s = serializers.CartGoodsSer(goods, many=True)
            return Response(s.data)