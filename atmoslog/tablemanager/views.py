#Imports
from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import db_interface

import re

def index(request):
	return HttpResponse("Hello, world. You're at the log manager.")

def settings(request):
	return HttpResponse("Settings")

def log(request):
	context = {}
	return render(request, 'tablemanager/log.html', context)

def projectlog(request, projectname, tablename):
	#For navbar control
	if request.user.is_authenticated():
		user = request.user.get_username()
	else:
		user = ""

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
				if not request.POST.get('remember_me', None):
					request.session.set_expiry(0)
				return redirect('atmoslog_main.views.index')
			else:
				status = "inactive"
		else:
			status = "failed"
	return render(request, 'tablemanager/login.html', {"status" : status})

def logout_view(request):
	logout(request)
	return redirect('atmoslog_main.views.index')

def register_view(request):
	issues = []
	username = firstname = lastname = password = email = ""
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		email = request.POST['email']
		if len(username) < 4 or len(username) > 50:
			#Username must be 4-50 characters long
			issues.append("username_length")
		if re.match('^\w+$', username) is None and len(username) != 0:
			#Username can only contain characters and numbers and underscores
			issues.append("username_char")
		if len(password) < 6 or len(password) > 50:
			#Password must be 6-50 characters long
			issues.append("password_length")
		if re.match("^[A-Za-z]*$", firstname) is None:
			#Names can only contain letters and spaces
			issues.append("firstname_char")
		if re.match("^[A-Za-z]*$", lastname) is None:
			#Names can only contain letters and spaces
			issues.append("lastname_char")
		if re.match("^[A-Za-z@.]*$", email) is None or len(email) < 3:
			#Email invalid
			issues.append("email_char")

		#Sign the user up
		if len(issues) == 0:
			user = User.objects.create_user(username, email, password)
			if len(firstname) != 0:
				user.first_name = firstname
			if len(lastname) != 0:
				user.last_name = lastname
			user.save()
			#Redirect the user to the verification process
			#TO-DO
			return redirect('atmoslog_main.views.index')

	return render(request, 'tablemanager/register.html', {"issues" : issues})

def create_project(request):
	pass


def projectsettings(request, projectname):
	pass

@login_required(login_url='/login/')
def userpage(request):
	username = request.user.username

