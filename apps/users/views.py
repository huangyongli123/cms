from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView

from users.models import Area
from users.serializers import UserRegisterSerializer, AreaSerializer, SubAreaSerializer


def test(request):
    a=300

    return HttpResponse('tbest')


class UserRegisterView(CreateAPIView):
    '''用户注册'''
    serializer_class = UserRegisterSerializer


class AreaProvinceView(ListAPIView):  # 查询所有的省份
    queryset = Area.objects.filter(parent=None)  # 所有的省份
    serializer_class = AreaSerializer
    # 禁用分页功能
    pagination_class = None


class SubAreaView(RetrieveAPIView):  # 查询一个区域（城市和区县）
    queryset = Area.objects.all()
    serializer_class = SubAreaSerializer