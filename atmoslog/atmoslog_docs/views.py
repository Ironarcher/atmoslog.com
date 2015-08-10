from django.shortcuts import render
from django.http import *

# Views for documentation here

def docs_index(request):
	if request.user.is_authenticated():
		authenticated = True
		user = request.user
	else:
		authenticated = False
		user = None

	context = {
		"authenticated" : authenticated,
		"user" : user,
	}
	return render(request, 'atmoslog_docs/docs_home.html', context)

def webapi(request):
	if request.user.is_authenticated():
		authenticated = True
		user = request.user
	else:
		authenticated = False
		user = None

	context = {
		"authenticated" : authenticated,
		"user" : user,
	}
	return render(request, 'atmoslog_docs/webapi.html', context)

def getstarted(request):
	if request.user.is_authenticated():
		authenticated = True
		user = request.user
	else:
		authenticated = False
		user = None

	context = {
		"authenticated" : authenticated,
		"user" : user,
	}
	return render(request, 'atmoslog_docs/getstarted.html', context)

def python_api(request):
	if request.user.is_authenticated():
		authenticated = True
		user = request.user
	else:
		authenticated = False
		user = None

	context = {
		"authenticated" : authenticated,
		"user" : user,
	}
	return render(request, 'atmoslog_docs/python_api.html', context)