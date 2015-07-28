from django.shortcuts import render, redirect
from django.http import *

# Create your views here.

def index(request):
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
	return render(request, 'atmoslog_main/index.html', context)

def pricing(request):
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
	return render(request, 'atmoslog_main/pricing.html', context)
