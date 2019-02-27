from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps import goods


class CartAddSerializer(serializers.Serializer):
    """添加商品到购物车的序列化器"""
    goods_id = serializers.IntegerField(label='商品id')
    count = serializers.IntegerField(label='商品数量')
    selected = serializers.BooleanField(label='是否勾选')

    def validate(self, value):
        """判断添加到购物车的商品是否存在"""
        try:
            sku = goods.objects.get(id=value['goods_id'])
        except goods.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value


class CartGoodsSer(ModelSerializer):
    selected = serializers.BooleanField(label='勾选状态')
    count = serializers.IntegerField(label='商品数量')

    class Meta:
        model = goods
        fields = '__all__'

