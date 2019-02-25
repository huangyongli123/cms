from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from news.serializers import *
from news.models import News, NewsCategory


class NewsTopView(APIView):
    def get(self, request):
        slide_news = News.objects.exclude(img_url='').filter(is_slide=1)[0:3]

        top_news = News.objects.order_by('-create_time')[0:10]

        image_news = News.objects.exclude(img_url='').order_by("-click")[0:4]

        slide_news_s = NewsTOPSerializer(slide_news, many=True).data

        top_news_s = NewsTOPSerializer(top_news, many=True).data

        image_news_s = NewsTOPSerializer(image_news, many=True).data

        data = {
            "slide_news_s": slide_news_s,
            "top_news_s": top_news_s,
            "image_news_s": image_news_s,
        }
        return Response(data)


class CategoryView(APIView):
    def get(self, request):
        cate_query = NewsCategory.objects.filter(parent_id=0)  # 3个一级新闻对象
        data_list = []
        for cate in cate_query: # cate为每一个一级新闻对象
            cate_query_dict = CategorySerializer(cate).data
            cate_son_query = cate.newscategory_set.all() # 得到二级新闻对象
            ids_list = []
            for cate in cate_son_query: # cate为每一个二级新闻对象
                ids_list.append(cate.id)
            # [8, 9 ,10]第一个分类列表的二级分类ID的集合
            cate_query_dict["news"] = NewsTOPSerializer(News.objects.filter(category_id__in=ids_list).exclude(img_url='').order_by("-create_time")[0:4], many=True).data
            cate_query_dict["top8"] = NewsTOPSerializer(News.objects.filter(category_id__in=ids_list).order_by("-click")[0:8], many=True).data
            data_list.append(cate_query_dict)
        return Response(data_list)














