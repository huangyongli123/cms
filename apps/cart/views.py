import base64
import pickle
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView


from cart import serializers
from cart.serializers import CartAddSerializer
from goods.models import Goods


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
                redis.sadd('carts_selected_%s' % user.id, goods_id)
            # 响应序列化数据
                return Response({"count":sum([int(i) for i in redis.hvals('cart_%s'%user.id)])})
        return Response(status=301)

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # 连接redis数据库
            redis = get_redis_connection('cart')  # type:StrictRedis
            # 获取商品及其数量
            # cart_1 = {1: 2, 2: 2}  商品数量存储
            dict_cart = redis.hgetall('cart_%s' % user.id)
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
        else:#用户未登陆，操作cookie
            cart=request.COOKIES.get('cart')
            if cart:
                cart=pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart={}
            print('cookie',cart)
        goods = Goods.objects.filter(id__in=cart.keys())
        count = 0
        for good in goods:
            good.count = cart[good.id]['count']
            good.selected = cart[good.id]['selected']
            count += good.count
        s = serializers.CartGoodsSer(goods, many=True)
        return Response({'goods': s.data, "count": count})


    def put(self,request):
        """修改购物车的商品"""
        #创建序列化器，校验参数是否合法

        s=serializers.CartAddSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        #获取校验后的三个参数，sku_id count selected
        goods_id=s.validated_data.get('goods_id')
        count=s.validated_data.get('count')
        selected=s.validated_data.get('selected')
        #获取用户对象
        user=request.user
        #判断用户是否已经登陆
        if user.is_authenticated:
            #用户已经登陆，获取操作redis的StrictRedis对象
            strict_redis=get_redis_connection("cart")
            #修改商品的数量
            strict_redis.hset('cart_%s'%user.id,goods_id,count)
            #修改商品的勾选状态
            if selected:
                strict_redis.sadd('cart_selected_%s'%user.id,goods_id)
            else:
                strict_redis.srem('cart_selected_%s'%user.id,goods_id)
            #响应序列化数据

            return Response({"total_count":sum([int(i) for i in strict_redis.hvals('cart_%s'%user.id)])})
        else:#未登陆
            #1.从cookie中获取购物车信息
            cart=request.COOKIES.get('cart')
            if cart:
                cart=pickle.loads(base64.b64decode( cart.encode()))
            else:
                cart = {}
            print('cookie',cart)
            cart[goods_id]={
                'count':count,
                'selected':selected,
            }
            cart=base64.b64encode(pickle.dumps(cart)).decode()
            # cart=base64.b64encode(pickle.dumps(cart)).decode()
            #5.通过cookie保存购物车数据
            response=Response(s.data)
            response.set_cookie('cart',cart,60*60*24*365)


            return response

    def delete(self,request):
        """删除购物车里的商品"""
        #创建序列化器，校验参数sku_id是否合法
        s=serializers.CartDeleteSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        #获取校验后的goods_id
        goods_id=s.validated_data.get("goods_id")
        #获取用户对象
        user=request.user
        print(user)
        #通过cookie保存购物车数据（base64字符串）
        response=Response(status=204)
        if user.is_authenticated():
            #用户已经登陆，操作redis

            stript_redis=get_redis_connection("cart")
            #删除商品

            stript_redis.hdel("cart_%s"% user.id,goods_id)
            #删除商品的勾选状态
            stript_redis.srem('cart_selected_%s'%user.id,goods_id)

            #响应数据
            return response
        else:#未登陆，操作cookie
            cart=request.COOKIES.get('cart')
            if cart:
                cart=pickle.loads(base64.b64decode(cart.encode()))
                if goods_id in cart:
                    del cart[goods_id]

                    cart=base64.b64encode(pickle.dumps(cart)).decode()
                    response.set_cookie('cart',cart,60*60*24*365)
            return response


class CartSelectAllView(APIView):
    """
    购物车全选和全不选
    """

    def perform_authentication(self, request):
        """
        drf框架在视图执行前会调用此方法进行身份认证(jwt认证)
        如果认证不通过,则会抛异常返回401状态码
        问题: 抛异常会导致视图无法执行
        解决: 捕获异常即可
        """
        try:
            super().perform_authentication(request)
        except Exception:
            pass

    def put(self, request):
        """全选或全不选"""
        serializer = serializers.CartSelectAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data['selected']

        user = request.user
        if user.is_authenticated():
            # 用户已登录，在redis中保存
            #  cart_1 = {1: 2, 2: 2}
            # cart_selected_1 = {1}
            redis_conn = get_redis_connection('cart')
            # hkeys cart_1    (1, 2)    获取hash所有的字段名
            sku_id_list = redis_conn.hkeys('cart_%s' % user.id)  # （1, 2） bytes

            if selected:  # 全选
                redis_conn.sadd('cart_selected_%s' % user.id, *sku_id_list)
            else:  # 取消全选
                redis_conn.srem('cart_selected_%s' % user.id, *sku_id_list)
            return Response({'message': 'OK'})
        else:
            # cookie
            response = Response({'message': 'OK'})
            # 1. 从cookie中获取购物车信息
            cart = request.COOKIES.get('cart')
            # 2. base64字符串 -> 字典
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                # 3. 修改对应商品的选中状态
                # {1: {'count':2, 'selected':False}, 2: {'count':2, 'selected':False}}
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                # 4. 字典 --> base64字符串
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                # 5. 通过cookie保存购物车数据（base64字符串）
                response.set_cookie('cart', cookie_cart, constants.CART_COOKIE_EXPIRES)
            return response
