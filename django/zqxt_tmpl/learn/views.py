#-*- coding:utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse

# Create your views here.

def home1(request):
    string = u"我在自强学堂学习Django，用它来建网站"
    return render(request,'home.html',{'string':string})

def home2(request):
    TutorialList = ["html","css","jquery","python","django"]
    return render(request,"home.html",{"TutorialList":TutorialList})

def home3(request):
    List = map(str,range(100))
    return render(request,"home.html",{'List':List,'A':10,'B':11,'var':88})

def home(request):
    List = map(str,range(100))
    return render_to_response("home.html",{'List':List,'A':10,'B':11,'var':88})

def add(request,a,b):
    c = int(a)+ int(b)
    return HttpResponse(str(c))


