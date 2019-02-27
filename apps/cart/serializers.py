from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from goods.models import Goods


class CartAddSerializer(serializers.Serializer):
    """添加商品到购物车的序列化器"""
    sku_id = serializers.IntegerField(label='商品id')
    count = serializers.IntegerField(label='商品数量')
    selected = serializers.BooleanField(label='是否勾选')

    def validate(self, value):
        """判断添加到购物车的商品是否存在"""
        try:
            sku = SKU.objects.get(id=value['sku_id'])
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value


class CartGoodsSer(ModelSerializer):
    selected = serializers.BooleanField(label='勾选状态')
    count = serializers.IntegerField(label='商品数量')

    class Meta:
        model = Goods
        fields = '__all__'

