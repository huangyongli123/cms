from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
def test(request):

    b=3
    c=5
    return HttpResponse('test')