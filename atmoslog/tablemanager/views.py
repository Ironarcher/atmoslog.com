#Imports
from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import db_interface

import re
import math
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
		return HttpResponseRedirect('/login?next=/log/%s/%s/' % (projectname, tablename))

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
		name = projectname + '-' + tablename
		revisedtables = []
		#Cut off x characters from tablename to display
		#x = length of project name and the hyphen
		length = len(projectname) + 1
		for table in tables:
			revisedtables.append(table[length:])
			print(table)

		logset = db_interface.findlogs(projectname, tablename, 100)
		total_in_logset = len(logset)
		print(total_in_logset)
		loglists = []
		for i in range(10):
			newlist = []
			for l in range(10):
				if 10*i+l < total_in_logset:
					print(10*i+l)
					newlist.append(logset[(10*i)+l])
				else:
					newlist.append("")
			loglists.append(newlist)

		print(loglists[0])
		finalloglist = zip(loglists[0], loglists[1], loglists[2],
			loglists[3], loglists[4], loglists[5], loglists[6],
			loglists[7], loglists[8], loglists[9])

		#Compile list of all projects by the user and exclude the current one
		#TODO: Make a webpage that is a complete list of all the user's recently viewed projects,
		#owned projects, and a project search bar

		context = {
			'specific_project' : projectname, 
			'tablelist' : revisedtables,
			'specific_table' : tablename,
			'range' : range(10),
			'logs' : finalloglist,
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
	next = ""
	if request.GET:
		next = request.GET['next']
		print(next)

	if request.POST:
		first = False
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				status = "success"
				remember = request.POST.getlist('remember[]')
				if "remember" in remember:
					request.session.set_expiry(1209600)
				if next == "":
					return HttpResponseRedirect("/")
				else:
					return HttpResponseRedirect(next)
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
		"next" : next,
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
		return HttpResponseRedirect("/login/?next=/create/")
	else:
		authenticated = True
		user = request.user
	issues = []
	#Another variable: Access -> true = public && false = private
	name = description = ""
	if request.method == "POST":
		first = False
		name = request.POST['name']
		description = request.POST['description']
		creator = request.user.get_username()
		#TODO: fix the access (can only be private for some reason)
		access = request.POST.getlist('public[]')
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
		"authenticated" : authenticated,
		"user" : user,
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
			raise Http404("Project does not exist.n")
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
		return HttpResponseRedirect('/login?next=/log/%s' % projectname)

	#Verify that project exists
	tables = db_interface.gettables(projectname)
	if len(tables) == 0:
		raise Http404("Project does not exist.")
	else:
		projectfile = db_interface.getProject(projectname)

	#Verify post results and handle forms
	issues = []
	issues2 = []
	newname = quanqual = discretecontinuous = ""
	edit_name = projectname
	key_reset = False
	edit_description = projectfile['description']
	edit_access_final = projectfile['access']
	edit_default_tabletype = projectfile['default_tabletype']
	if request.method == "POST":
		if request.POST['formtype'] == 'create_table':
			edit_first = True
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
		elif request.POST['formtype'] == 'edit_project':
			first = True
			edit_first = False
			edit_name = request.POST['edit_name']
			edit_description = request.POST['edit_description']
			edit_access = request.POST.getlist('acc2[]')
			edit_default_tabletype = request.POST['edit_quanqual']
			print(edit_default_tabletype)

			if len(edit_name) < 4 or len(edit_name) > 50:
				#Project name must be 4-50 characters long.
				issues2.append("name_length")
			if re.match('^\w+$', edit_name) is None and len(edit_name) != 0:
				#Project name can only contain characters and numbers and underscores.
				issues2.append("name_char")
			if len(edit_description) > 500:
				#Description is optional
				#If description must be under 500 characters long.
				issues2.append("description_length")
			if edit_name != projectname and db_interface.checkProjectExists(edit_name):
				issues2.append("name_taken")

			#Update the project:
			if len(issues2) == 0:
				if "public" in edit_access:
					edit_access_final = "public"
				else:
					edit_access_final = "private"
				db_interface.updateProject(projectname, edit_name, edit_access_final,
					edit_description, edit_default_tabletype)
				return HttpResponseRedirect('/log/%s' % edit_name)
		elif request.POST['formtype'] == "reset_key":
			#Reset the project's secret key
			key_reset = True
			first = True
			edit_first = True
			db_interface.resetKey(projectname)
		elif request.POST['formtype'] == "change_status":
			first = True
			edit_first = True
			if projectfile['status'] == "running":
				db_interface.changeStatus(projectname, "stopped")
			elif projectfile['status'] == "stopped":
				db_interface.changeStatus(projectname, "running")
			return HttpResponseRedirect('/log/%s' % projectname)
	else:
		quanqual = db_interface.getTabletypeDefault(projectname)
		first = True
		edit_first = True

	revisedtables = []
	#Cut off x characters from tablename to display
	#x = length of project name and the hyphen
	length = len(projectname) + 1
	for table in tables:
		revisedtables.append(table[length:])

	context = {
		'specific_project' : projectname, 
		'project_description' : projectfile['description'],
		'project_funds' : centsToUSD(projectfile['usd_cents']),
		'project_access' : projectfile['access'],
		'project_free_logs' : projectfile['free_logs'],
		'project_date_created' : timeSince(projectfile['datecreated']),
		'project_last_added_free_logs' : timeSince(projectfile['last_added_free_logs']),
		'secret_key' : projectfile['secret_key'],
		'project_total_logs' : projectfile['total_logs'],
		'project_popularity' : projectfile['popularity'],
		'project_status' : projectfile['status'],
		'tablelist' : revisedtables,
		'username' : user,
		'first' : first,
		'edit_first' : edit_first,
		'reset_key' : key_reset,
		'newname' : newname,
		'quanqual' : quanqual,
		'discretecontinuous' : discretecontinuous,
		'edit_name': edit_name,
		'edit_description' : edit_description,
		'edit_access_final' : edit_access_final,
		'edit_default_tabletype' : edit_default_tabletype,
		'issues' : issues,
		'issues2' : issues2,
		'projectlist' : projectlist,
		'myproject' : myproject,
	}

	return render(request, "tablemanager/project_details.html", context)

#Login is required to view this page
def user_page(request):
	if request.user.is_authenticated():
		authenticated = True
		user = request.user
		username = request.user.get_username()
		#get the firstname and lastname

		userobj = User.objects.get(username=user)
		firstname = userobj.first_name
		lastname = userobj.last_name
		email = userobj.email
		about_me = None
		favorite_language = None
		join_date = None

		context = {
		"authenticated" : authenticated,
		"user" : user,
		"firstname" : firstname,
		"lastname" : lastname,
		"email" : email,
		"about_me" : about_me,
		"favorite_language" : favorite_language,
		"join_date" : join_date,
		"user_projects" : db_interface.getUserProjects(username),
		}
		return render(request, 'tablemanager/account.html', context)
	else:
		return HttpResponseRedirect('/login/?next=/account/')

def search(request):
	query = ""
	searchtype = "projects"
	if request.GET:
		query = request.GET['query']
		if len(request.GET) == 2 and 'searchtype' in request.GET:
			searchtype = request.GET['searchtype']

	if request.POST:
		if 'query' in request.POST:
			query = request.POST['query']
		if 'searchtype' in request.POST:
			searchtype = request.POST['searchtype']

	if request.user.is_authenticated():
		authenticated = True
		user = request.user
		results = db_interface.overallProjectSearch_withuser(query, user.get_username(), 20)
	else:
		authenticated = False
		user = None
		results = db_interface.overallProjectSearch(query, 20)
	print('warning query')

	names = []
	descriptions = []
	popularities = []
	total_logs = []
	admins = []
	for project in results:
		names.append(project['name'])
		descriptions.append(project['description'])
		popularities.append(normalize(project['popularity']))
		total_logs.append(normalize(project['total_logs']))
		admins.append(project['admins'][0])
	projects = zip(names, descriptions, popularities, total_logs, admins)
	print(len(names))

	context = {
		"authenticated" : authenticated,
		"user" : user,
		"results" : projects,
	}
	return render(request, 'tablemanager/search.html', context)

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
		t = str(diff)
		if t == "1":
			return "1 second ago"
		else:
			return "%s seconds ago" % str(diff)
	elif diff < 3600:
		#minutes
		t = str(diff/60)
		if t == "1":
			return "1 minute ago"
		else:
			return "%s minutes ago" % str(diff/60)
	elif diff < 86400:
		#hours
		t = str(diff/3600)
		if t == "1":
			return "1 hour ago"
		else:
			return "%s hours ago" % str(diff/3600)
	elif diff < 2626560:
		#days with 30.4 days in a month average
		t = str(diff/86400)
		if t == "1":
			return "1 day ago"
		else:
			return "%s days ago" % str(diff/86400)
	elif diff < 31518720:
		#months 
		t = str(diff/2626560)
		if t == "1":
			return "1 month ago"
		else:
			return "%s months ago" % str(diff/2626560)
	else:
		#years
		t = str(diff/31518720)
		if t == "1":
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

def normalize(number):
	if number > 1000000000:
		return str(math.floor(number/1000000000)) + "b"
	elif number > 1000000:
		return str(math.floor(number/1000000)) + "m"
	elif number > 1000:
		return str(math.floor(number/1000)) + "k"
	else:
		return str(number)
