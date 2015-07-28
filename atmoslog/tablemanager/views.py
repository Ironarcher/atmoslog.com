#Imports
from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import db_interface

import re
import time

def index(request):
	#For navbar control
	if request.user.is_authenticated():
		user = request.user.get_username()
	else:
		user = "World"
	return HttpResponse("Hello, %s. You're at the log manager." % user)

def projectlog(request, projectname, tablename):
	#For navbar control and user access verification
	if request.user.is_authenticated():
		user = request.user.get_username()
		access = db_interface.getProjectAccess(projectname) 
		if access is None:
			raise Http404("Project does not exist.")
		elif access == "private":
			myproject = True
			projectlist = db_interface.getUserProjects(user) 
			print projectlist
			print user
			if projectname in projectlist:
				projectlist.remove(projectname)
			else:
				raise Http404("User access denied.")
		elif access == "public":
			projectlist = db_interface.getUserProjects(user)
			if projectname in projectlist:
				myproject = True
				projectlist.remove(projectname)
			else:
				myproject = False

	else:
		return HttpResponseRedirect('/login/tables-%s-%s/' % (projectname, tablename))

	issues = []
	newname = quanqual = discretecontinuous = ""
	if request.method == "POST":
		if request.POST['formtype'] == "create_table":
			first = False
			edit_first = True
			newname = request.POST['name']
			quanqual = request.POST['quanqual']
			if len(newname) > 50 or len(newname) < 3:
				issues.append("name_length")
			if re.match('^\w+$', newname) is None and len(newname) != 0:
				issues.append("name_char")

			if len(issues) == 0:
				#Create the table type to help with graphing later
				db_interface.createTable(projectname, newname, quanqual)
				return HttpResponseRedirect('/log/%s/%s/' % (projectname, newname))
		elif request.POST['formtype'] == 'edit_project':
			first = True
			edit_first = False
	else:
		quanqual = db_interface.getTabletypeDefault(projectname)
		first = True
		edit_first = True


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

		#Compile list of all projects by the user and exclude the current one
		#TODO: Make a webpage that is a complete list of all the user's recently viewed projects,
		#owned projects, and a project search bar

		context = {
			'specific_project' : projectname, 
			'tablelist' : revisedtables,
			'specific_table' : tablename,
			'logs' : db_interface.findlogs(projectname, tablename, 20),
			'logcount' : db_interface.getlogcount(projectname, tablename),
			'username' : user,
			'first' : first,
			'newname' : newname,
			'quanqual' : quanqual,
			'discretecontinuous' : discretecontinuous,
			'issues' : issues,
			'projectlist' : projectlist,
			'myproject' : myproject,
		}

		if name in tables:
			return render(request, 'tablemanager/table_view.html', context)
		else:
			#raise Http404("Table in this project does not exist.")
			return render(request, 'tablemanager/table_does_not_exist.html', context)

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
				#TODO: Still not working (request.session.set_expiry)
				#is not closing the session
				remember = request.POST.getlist('remember')
				if "remember" not in remember:
					request.session.set_expiry(0)
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
		#TODO: fix the access (can only be private for some reason)
		access = request.POST.getlist('public')
		if "public" in access:
			access_final = "public"
		else:
			access_final = "private"
		print(access)
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
			db_interface.createProject(name, creator, access_final, description)
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

#Login is required to view this page
def project_settings(request, projectname):
	#For navbar control and user access verification
	if request.user.is_authenticated():
		user = request.user.get_username()
		access = db_interface.getProjectAccess(projectname) 
		if access is None:
			raise Http404("Project does not exist.")
		elif access == "private":
			myproject = True
			projectlist = db_interface.getUserProjects(user) 
			print projectlist
			print user
			if projectname in projectlist:
				projectlist.remove(projectname)
			else:
				raise Http404("User access denied.")
		elif access == "public":
			projectlist = db_interface.getUserProjects(user)
			if projectname in projectlist:
				myproject = True
				projectlist.remove(projectname)
			else:
				myproject = False

	else:
		return HttpResponseRedirect('/login/tables-%s-%s/' % (projectname, tablename))

	issues = []
	newname = quanqual = discretecontinuous = ""
	if request.method == "POST":
		first = False
		newname = request.POST['name']
		quanqual = request.POST['quanqual']
		if len(newname) > 50 or len(newname) < 3:
			issues.append("name_length")
		if re.match('^\w+$', newname) is None and len(newname) != 0:
			issues.append("name_char")

		if len(issues) == 0:
			#Create the table type to help with graphing later
			db_interface.createTable(projectname, newname, quanqual)
			return HttpResponseRedirect('/log/%s/%s/' % (projectname, newname))
	else:
		quanqual = db_interface.getTabletypeDefault(projectname)
		first = True

	tables = db_interface.gettables(projectname)
	if len(tables) == 0:
		raise Http404("Project does not exist.")
	else:
		projectfile = db_interface.getProject(projectname)
		revisedtables = []
		#Cut off x characters from tablename to display
		#x = length of project name and the hyphen
		length = len(projectname) + 1
		for table in tables:
			revisedtables.append(table[length:])

		#TODO: Make a webpage that is a complete list of all the user's recently viewed projects,
		#owned projects, and a project search bar 

		context = {
			'specific_project' : projectname, 
			'project_description' : projectfile['description'],
			'project_funds' : centsToUSD(projectfile['usd_cents']),
			'project_access' : projectfile['access'],
			'project_free_logs' : projectfile['free_logs'],
			'project_date_created' : timeSince(projectfile['datecreated']),
			'secret_key' : projectfile['secret_key'],
			'tablelist' : revisedtables,
			'username' : user,
			'first' : first,
			'newname' : newname,
			'quanqual' : quanqual,
			'discretecontinuous' : discretecontinuous,
			'issues' : issues,
			'projectlist' : projectlist,
			'myproject' : myproject,
		}

		return render(request, "tablemanager/project_details.html", context)

#Login is required to view this page
def user_page(request):
	username = request.user.get_username()

	return None

def check_user_exists(username):
	if User.objects.filter(username=username).exists():
		return True
	else:
		return False

def centsToUSD(cents):
	dollars = str(cents/100.00)
	#For example: 3410 returns 34.1 not 34.10
	verify = dollars.split(".")
	if len(verify[1]) == 1:
		dollars = dollars + "0"

	return "$" + dollars

def timeSince(unixtime):
	diff = int(time.time()) - unixtime
	if diff < 60:
		#seconds
		time = str(diff)
		if time == "1":
			return "1 second ago"
		else:
			return "%s seconds ago" % str(diff)
	elif diff < 3600:
		#minutes
		time = str(diff/60)
		if time == "1":
			return "1 minute ago"
		else:
			return "%s minutes ago" % str(diff/60)
	elif diff < 86400:
		#hours
		time = str(diff/3600)
		if time == "1":
			return "1 hour ago"
		else:
			return "%s hours ago" % str(diff/3600)
	elif diff < 2626560:
		#days with 30.4 days in a month average
		time = str(diff/86400)
		if time == "1":
			return "1 day ago"
		else:
			return "%s days ago" % str(diff/86400)
	elif diff < 31518720:
		#months 
		time = str(diff/2626560)
		if time == "1":
			return "1 month ago"
		else:
			return "%s months ago" % str(diff/2626560)
	else:
		#years
		time = str(diff/31518720)
		if time == "1":
			return "1 year ago"
		else:
			return "%s years ago" % str(diff/31518720)

def logsToCents(logs):
	cents = 0
	if logs > 100000000:
		diff = logs - 100000000
		cents = cents + ((logs-100000000) * 1.5 / 10000)
		logs = logs - diff
	if logs > 10000000:
		diff = logs - 10000000
		cents = cents + ((logs-10000000) * 3 / 10000)
		logs = logs - diff
	cents = cents + (logs * 6 / 10000)
	return cents

