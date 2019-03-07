from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin, RetrieveModelMixin, \
    UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.models import Area, Address
from users.serializers import UserRegisterSerializer, AreaSerializer, SubAreaSerializer, AddressSerializer


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


class AddressAPIViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    # permission_classes = (IsAuthenticated,)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({"addresses": serializer.data, "default_address_id": request.user.default_address_id})
        # return Response(serializer.data)

    @action(methods=['PUT'], detail=True)
    def status(self, request, pk):
        user = request.user
        try:
            Address.objects.get(id=pk, user=user)
        except:
            raise ValidationError('该地址不存在或者不属于该用户')
        user.default_address_id = pk
        user.save()
        return Response(status=204)