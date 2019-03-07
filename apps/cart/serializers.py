from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from goods.models import Goods


class CartAddSerializer(serializers.Serializer):
    """添加商品到购物车的序列化器"""
    goods_id = serializers.IntegerField(label='商品id')
    count = serializers.IntegerField(label='商品数量')
    selected = serializers.BooleanField(label='是否勾选')

    def validate(self, value):
        """判断添加到购物车的商品是否存在"""
        try:
            Goods.objects.get(id=value['goods_id'])
        except Goods.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value


class CartGoodsSer(ModelSerializer):
    selected = serializers.BooleanField(label='勾选状态')
    count = serializers.IntegerField(label='商品数量')

    class Meta:
        model = Goods
        fields = ('id', 'sell_price', 'count', 'selected','title','category','img_url')


class CartDeleteSerializer(serializers.Serializer):
    """
    删除购物车数据序列化器
    """
    goods_id = serializers.IntegerField(label='商品id', min_value=1)

    def validate_goods_id(self, value):
        try:
            sku = Goods.objects.get(id=value)
        except Goods.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value

class CartSelectAllSerializer(serializers.Serializer):
    """
    购物车全选
    """
    selected = serializers.BooleanField(label='全选')


