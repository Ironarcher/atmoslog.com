from django.shortcuts import render, redirect
from django.http import *

# Create your views here.

def index(request):
	context = {}
	return render(request, 'atmoslog_main/index.html', context)
