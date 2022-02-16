from django.shortcuts import render
from django.http import HttpResponse


def savings(request):
    return HttpResponse('Oszczędności')


def budget(request):
    return HttpResponse('Budżet')
