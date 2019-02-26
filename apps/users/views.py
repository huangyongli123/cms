from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
def test(request):
    a=300

    return HttpResponse('tbest')