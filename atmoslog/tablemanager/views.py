from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import db_interface

def index(request):
	return HttpResponse("Hello, world. You're at the log manager.")

def settings(request):
	return HttpResponse("Settings")

def log(request):
	context = {}
	return render(request, 'tablemanager/log.html', context)

def projectlog(request, projectname, tablename):
	tables = db_interface.gettables(projectname)
	if len(tables) == 0:
		raise Http404("Project does not exist.")
	else:
		name = projectname + '-' + tablename
		revisedtables = []
		#Cut off x characters from tablename to display
		#x = length of project name and the hyphen
		length = len(projectname) + 1
		for table in tables:
			revisedtables.append(table[length:])
		if name in tables:
			context = {
				'specific_project' : projectname, 
				'tablelist' : revisedtables,
				'specific_table' : tablename,
				'logs' : db_interface.findlogs(projectname, tablename, 20),
				'logcount' : db_interface.getlogcount(projectname, tablename)
			}
			return render(request, 'tablemanager/tables.html', context)
		else:
			raise Http404("Table in this project does not exist.")

def login_view(request):
	status = "started"
	username = password = ""
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				status = "success"
				return redirect('atmoslog_main.views.index')
			else:
				status = "inactive"
		else:
			status = "failed"
	return render(request, 'tablemanager/login.html', {"status" : status})

def logout_view(request):
	logout(request)

def register_view(request):
	pass

def projectsettings(request, projectname):
	pass

@login_required(login_url='/login/')
def userpage(request):
	username = request.user.username

