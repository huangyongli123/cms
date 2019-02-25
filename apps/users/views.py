from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView

from users.serializers import UserRegisterSerializer


def test(request):
    a=2


    return HttpResponse('tbest')

class UserRegisterView(CreateAPIView):
    """用户注册接口"""
    serializer_class = UserRegisterSerializer