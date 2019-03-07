from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from news.models import News, NewsCategory
from users.models import Address


class NewsTOPSerializer(ModelSerializer):

    class Meta:
        model = News
        fields = "__all__"


class SonsCategorySerializer(ModelSerializer): # 二级新闻序列化器
    class Meta:
        model = NewsCategory
        fields = ("id", "title")


class CategorySerializer(ModelSerializer): # 一级新闻序列化器
    newscategory_set = SonsCategorySerializer(many=True, read_only=True)

    class Meta:
        model = NewsCategory
        fields = ("id", "title", "newscategory_set")








