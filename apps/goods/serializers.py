from rest_framework.serializers import ModelSerializer

from goods.models import GoodsCategory, Goods, GoodsAlbum


class sonGoodsCateSer(ModelSerializer):

    class Meta:
        model=GoodsCategory
        fields=('id','title',)


class GoodsCateSer(ModelSerializer):
    goodscategory_set=sonGoodsCateSer(many=True,read_only=True)

    class Meta:
        model=GoodsCategory
        fields=('id','title','goodscategory_set')

class GoodsSer(ModelSerializer):
    class Meta:
        model=Goods
        fields='__all__'

class ImgSer(ModelSerializer):
    class Meta:
        model=GoodsAlbum
        fields='__all__'
