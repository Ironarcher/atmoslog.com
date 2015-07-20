from django.shortcuts import render
from django.http import HttpResponse
import db_interface

# Create your views here.

def index(request):
	return HttpResponse("Hello, world. You're at the log manager.")

def settings(request):
	return HttpResponse("Settings")

def log(request):
	context = {}
	return render(request, 'tablemanager/log.html', context)

def projectlog(request, projectname):
	raise Http404("Project does not exist")
	return render(request, 'tablemanager/tables.html', context)
