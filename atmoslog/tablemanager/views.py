from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
	return HttpResponse("Hello, world. You're at the log manager.")

def settings(request):
	return HttpResponse("Settings")

def log(request):
	context = {}
	return render(request, 'tablemanager/log.html', context)