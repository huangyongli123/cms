"""cms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from users import views
from users.views import AddressAPIViewSet

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^test/$', views.test),
    url(r'^register/$', views.UserRegisterView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^areas/$', views.AreaProvinceView.as_view()),
    url(r'^areas/(?P<pk>\d+)/$', views.SubAreaView.as_view()),

]
router = DefaultRouter()
# 参数1: 路由访问的前缀
# 参数2: 视图集
# 参数3: 路由名称的前缀, 可以省略不配
router.register(r'addresses', AddressAPIViewSet, base_name='address')

# router.urls: 生成出来的路由配置项
urlpatterns += router.urls
print(urlpatterns)