from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework.views import APIView

from goods import serializers
from goods.models import GoodsCategory, Goods, GoodsAlbum
from goods.serializers import GoodsSer


class RecommendView(APIView):
    def get(self,request):
        red_lis=Goods.objects.filter(is_red__exact=1).all()[0:4]
        data_lis=serializers.GoodsSer(red_lis,many=True)
        return Response(data_lis.data)

class GoodsView(APIView):
    def get(self,request):
        category_query=GoodsCategory.objects.filter(parent_id=0)
        data_dict=[]
        for cate in category_query:
            category_query_dict = serializers.GoodsCateSer(cate).data
            son_cate=cate.goodscategory_set.all()
            ids_list=[]
            #做一个二级分类id列表，判断商品是否在这个类别id列表中
            for i in son_cate:
                ids_list.append(i.id)
            category_query_dict['goods']=serializers.GoodsSer(Goods.objects.filter(category_id__in=ids_list).exclude(img_url='').order_by('-create_time')[0:5],many=True).data
            data_dict.append(category_query_dict)
        return Response(data_dict)

class GoodslistView(APIView):
    def get(self,request):
        category_id=request.GET.get('category')
        cate=GoodsCategory.objects.get(id=category_id)
        #判断是二级分类还是一级分类
        if cate.parent_id==0:
            #一级分类，#获取一级分类以下的二级分类对象
            next_cates = GoodsCategory.objects.filter(parent_id__exact=category_id).all()
            next_cates_lis = []
            for i in next_cates:
                next_cates_lis.append(i.id)

            goods_lis = Goods.objects.filter(category_id__in=next_cates).all()


            category={
                'id':cate.id,
                'title':cate.title
            }
        else:
            #二级分类
            goods_lis=Goods.objects.filter(category_id__exact=category_id).all()
            # 分类信息
            category = {
                'parent':{
                    'id':cate.parent.id,
                    'title':cate.parent.title
                },
                'id':cate.id,
                'title':cate.title
            }


        data_lis = serializers.GoodsSer(goods_lis, many=True)
        data={
            'goods':data_lis.data,
            'category':category
        }

        return Response(data)

class GoodsDetailView(APIView):
    def get(self,request):
        id=request.GET.get('id')
        goods_obj=Goods.objects.get(id=id)
        goods_ser=serializers.GoodsSer(goods_obj)
        #添加商品轮播图
        img_lis=GoodsAlbum.objects.filter(goods_id=id)
        imgs=serializers.ImgSer(img_lis,many=True)

        #添加商品的一级二级类别
        cate_obj=GoodsCategory.objects.get(id=goods_obj.category_id)
        cate=serializers.GoodsCateSer(cate_obj)
        cate_obj_parent=serializers.GoodsCateSer(cate_obj.parent).data
        cates=cate.data
        del cate_obj_parent['goodscategory_set']
        cates['parent']=cate_obj_parent

        goods=goods_ser.data
        goods['goodsalbum_set']=imgs.data
        goods['category']=cates
        return Response(goods)
