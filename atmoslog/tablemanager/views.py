#Imports
from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import db_interface

import re

def index(request):
	#For navbar control
	if request.user.is_authenticated():
		user = request.user.get_username()
	else:
		user = "World"
	return HttpResponse("Hello, %s. You're at the log manager." % user)

def projectlog(request, projectname, tablename):
	#For navbar control
	if request.user.is_authenticated():
		user = request.user.get_username()
	else:
		return HttpResponseRedirect('/login/tables-%s-%s/' % (projectname, tablename))

	issues = []
	newname = quanqual = discretecontinuous = ""
	if request.method == "POST":
		first = False
		newname = request.POST['name']
		quanqual = request.POST['quanqual']
		discretecontinuous = request.POST['discretecontinuous']
		if len(newname) > 50 or len(newname) < 3:
			issues.append("name_length")
		if re.match('^\w+$', newname) is None and len(newname) != 0:
			issues.append("name_char")

		if len(issues) == 0:
			#Create the table type to help with graphing later
			print(quanqual)
			print(discretecontinuous)
			if quanqual == "qualitative":
				tabletype = "qualitative"
			elif quanqual == "quantitative" and discretecontinuous == "discrete":
				tabletype = "quantitative_discrete"
			elif quanqual == "quantitative" and discretecontinuous == "continuous":
				tabletype = "quantitative_continuous"
			else:
				print('Critical error')
				return
			#Create the table
			print("creating new table")
			db_interface.createTable(projectname, newname, tabletype)
			return HttpResponseRedirect('/log/%s/%s/' % (projectname, newname))
	else:
		first = True

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
			print(table)
		if name in tables:
			context = {
				'specific_project' : projectname, 
				'tablelist' : revisedtables,
				'specific_table' : tablename,
				'logs' : db_interface.findlogs(projectname, tablename, 20),
				'logcount' : db_interface.getlogcount(projectname, tablename),
				'username' : request.user.get_username(),
				'first' : first,
				'newname' : newname,
				'quanqual' : quanqual,
				'discretecontinuous' : discretecontinuous,
				'issues' : issues,
			}
			return render(request, 'tablemanager/tables.html', context)
		else:
			raise Http404("Table in this project does not exist.")

def login_view(request):
	status = "started"
	username = password = ""
	if request.method == "POST":
		first = False
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				status = "success"
				#if not request.POST.get('remember_me', None):
				#	request.session.set_expiry(0)
				#if next.startswith("tables-"):
				#	parts = next.split("-")
				#	return HttpResponseRedirect("/log/%s/%s/" % (parts[1], parts[2]))
				#else:
				#	return HttpResponseRedirect("/")
				return HttpResponseRedirect("/")
			else:
				status = "inactive"
		else:
			status = "failed"
	else:
		first = True
	context = {
		"status" : status,
		"first" : first,
		"username_init" : username,
		"password_init" : password,
		#"next" : next,
	}
	return render(request, 'tablemanager/login.html', context)

def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")

def register_view(request):
	issues = []
	username = firstname = lastname = password = email = ""
	if request.method == "POST":
		first = False
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
		if check_user_exists(username):
			#User already exists
			issues.append("username_taken")

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
			return HttpResponseRedirect("/")
	else:
		first = True

	context = {
		"issues" : issues,
		"first" : first,
		"username_init" : username,
		"password_init" : password,
		"firstname_init" : firstname,
		"lastname_init" : lastname,
		"email_init" : email,
	}
	return render(request, 'tablemanager/register.html', context)

def create(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/login/")
	issues = []
	#Another variable: Access -> true = public && false = private
	name = description = ""
	if request.method == "POST":
		first = False
		name = request.POST['name']
		description = request.POST['description']
		creator = request.user.get_username()
		access = request.POST.get('public', None)
		if len(name) < 4 or len(name) > 50:
			#Project name must be 4-50 characters long.
			issues.append("name_length")
		if re.match('^\w+$', name) is None and len(name) != 0:
			#Project name can only contain characters and numbers and underscores.
			issues.append("name_char")
		if len(description) > 500:
			#Description is optional
			#If description must be under 500 characters long.
			issues.append("description_length")
		if db_interface.checkProjectExists(name):
			issues.append("name_taken")

		#Create the project:
		if len(issues) == 0:
			if access:
				access_real = 'public'
			else:
				access_real = 'private'
			db_interface.createProject(name, creator, access, description)
			return HttpResponseRedirect('/log/%s' % name)
	else:
		first = True
	context = {
		"issues" : issues,
		"first" : first,
		"name_init" : name,
		"description_init": description,
	}
	return render(request, 'tablemanager/create_project.html', context)

#@login_required(redirect_)
def project_settings(request, projectname):
	return HttpResponse("work in progress")

@login_required(login_url='/login/')
def user_page(request):
	username = request.user.get_username()

	return None

def check_user_exists(username):
	if User.objects.filter(username=username).exists():
		return True
	else:
		return False

