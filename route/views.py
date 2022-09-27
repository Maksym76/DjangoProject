from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    return HttpResponse('Ok!')


def route_datail(request, id):
    return HttpResponse('Ok!')


def route_reviews(request, id):
    return HttpResponse('Ok!')


def route_add(request):
    return HttpResponse('Ok!')


def route_add_event(request, id):
    return HttpResponse('Ok!')


def event_handler(request, id):
    return HttpResponse('Ok!')
