from django.shortcuts import render, redirect
from django.http import *

from .models import Feedback

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

#Ajax method
def send_feedback(request):
	if request.GET:
		if 'text' in request.GET:
			resp = request.GET['text']
	if request.user.is_authenticated():
		author = request.user.get_username()
	else:
		author = ""

	f = Feedback(text=resp, username_author=author)
	f.save()
	return HttpResponse("success")
