#Imports
from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import db_interface

import re
import math
import json
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
		if projectname + "-" + tablename not in db_interface.gettables(projectname):
			return HttpResponseRedirect('/log/%s' % (projectname, ))
		if access is None:
			raise Http404("Project does not exist.")
		elif access == "private":
			myproject = True
			projectlist = db_interface.getUserProjects(user) 
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

	#Recently viewed project handler
	addRecentProject(request.user.profile, projectname)

	issues = []
	issues2 = []
	newname = quanqual = discretecontinuous = ""
	tables = db_interface.gettables(projectname)
	name = projectname + '-' + tablename
	revisedtables = []
	#Cut off x characters from tablename to display
	#x = length of project name and the hyphen
	length = len(projectname) + 1
	for table in tables:
		revisedtables.append(table[length:])

	edit_name = tablename
	edit_tabletype = db_interface.getTabletype(projectname, tablename)
	default_tab = "analysis"

	if request.method == "POST":
		if request.POST['formtype'] == 'create_table':
			first = False
			edit_first = True
			newname = request.POST['name']
			quanqual = request.POST['quanqual']
			if len(newname) > 50 or len(newname) < 3:
				issues.append("name_length")
			if re.match('^\w+$', newname) is None and len(newname) != 0:
				issues.append("name_char")
			if newname in revisedtables:
				issues.append("name_taken")

			if len(issues) == 0:
				#Create the table type to help with graphing later
				db_interface.createTable(projectname, newname, quanqual)
				return HttpResponseRedirect('/log/%s/%s/' % (projectname, newname))
		elif request.POST['formtype'] == 'edit_table':
			first = True
			edit_first = False
			edit_name = request.POST['edit_name']
			edit_tabletype = request.POST['edit_quanqual']

			if len(edit_name) < 3 or len(edit_name) > 50:
				#Table name must be 4-50 characters long.
				issues2.append("name_length")
			if re.match('^\w+$', edit_name) is None and len(edit_name) != 0:
				#Table name can only contain characters and numbers and underscores.
				issues2.append("name_char")
			if edit_name in revisedtables and edit_name != tablename:
				issues2.append("name_taken")

			#Update the project:
			if len(issues2) == 0:
				db_interface.updateTable(projectname, tablename, edit_name, edit_tabletype)
				return HttpResponseRedirect('/log/%s/%s/' % (projectname, edit_name))
			else:
				default_tab = "settings"
		elif request.POST['formtype'] == 'delete_table':
			db_interface.deleteTable(projectname, tablename)
			return HttpResponseRedirect('/log/%s' % projectname)
	else:
		quanqual = db_interface.getTabletypeDefault(projectname)
		first = True
		edit_first = True

	logset = db_interface.findlogs(projectname, tablename, 100)
	total_in_logset = len(logset)
	loglists = []
	for i in range(10):
		newlist = []
		for l in range(10):
			if 10*i+l < total_in_logset:
				newlist.append(logset[(10*i)+l])
			else:
				newlist.append("")
		loglists.append(newlist)

	finalloglist = zip(loglists[0], loglists[1], loglists[2],
		loglists[3], loglists[4], loglists[5], loglists[6],
		loglists[7], loglists[8], loglists[9])

	rows =  db_interface.getFrequency_limit(projectname, tablename, 10)
	log_row = []
	log_count = []
	for row in rows:
		if 'Other' in row:
			log_row.append("Other")
			log_count.append(row['Other'])
		else:
			log_row.append(row['log'])
			log_count.append(row['count'])
	freq_log = zip(log_row, log_count)

	tot_logs = db_interface.getlogcount(projectname, tablename)
	ch1_data = []
	type_amt = 0
	ch3_data = []

	ch2_data = db_interface.getTimeGraph_alltime(projectname, tablename)
	if edit_tabletype == "quantitative_continuous":
		ch3_data = db_interface.getHistogram(projectname, tablename)
	else:
		if tot_logs > 0:
			rows2 = db_interface.getFrequency_limit(projectname, tablename, 4)
			for row in rows2:
				type_amt = type_amt + 1
				if 'Other' in row:
					ch1_data.append("Other")
					percentage = (float(row['Other'])/tot_logs)*100
					ch1_data.append(round(percentage))
				else:
					if row['log'] is not None:
						if row['log'].isspace():
							ch1_data.append("blank")
						else:
							ch1_data.append(row['log'])
					percentage = (float(row['count'])/tot_logs)*100
					ch1_data.append(round(percentage))

	context = {
		'specific_project' : projectname, 
		'tablelist' : revisedtables,
		'specific_table' : tablename,
		'logs' : finalloglist,
		'logcount' : tot_logs,
		'username' : user,
		'first' : first,
		'newname' : newname,
		'quanqual' : quanqual,
		'discretecontinuous' : discretecontinuous,
		'issues' : issues,
		'projectlist' : projectlist,
		'lenprojectlist' : len(projectlist),
		'myproject' : myproject,
		'freq_log' : freq_log,
		'ch1_data' : ch1_data,
		'type_amt' : type_amt,
		'tooltipTemplate' : '"<%=label%>: <%= value %>%"',
		'endtime' : int(time.time()),
		'ch2_data' : ch2_data[0],
		'time_scale' : ch2_data[1],
		'edit_first' : edit_first,
		'issues2' : issues2,
		'edit_name' : edit_name,
		'edit_tabletype' : edit_tabletype,
		'default_tab' : default_tab,
		'ch3_data' : ch3_data,
	}

	if name in tables:
		return render(request, 'tablemanager/table_view.html', context)
	else:
		#raise Http404("Table in this project does not exist.")
		return render(request, 'tablemanager/table_does_not_exist.html', context)

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
		access = request.POST.getlist('public[]')
		if "public" in access:
			access_final = "public"
		else:
			access_final = "private"
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

			#Add this project to liked projects
			userp = request.user.profile
			try:
				projlist = json.decoder.JSONDecoder().decode(userp.liked_projects)
			except ValueError:
				projlist = []
			projlist.append(name)
			userp.liked_projects = json.dumps(projlist)
			userp.save()
			db_interface.likeProject(name)
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
		revisedtables = []
		#Cut off x characters from tablename to display
		#x = length of project name and the hyphen
		length = len(projectname) + 1
		for table in tables:
			revisedtables.append(table[length:])

		#Recently viewed project handler
		addRecentProject(request.user.profile, projectname)

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
			if newname in revisedtables:
				issues.append("name_taken")
			if len(issues) == 0:
				#Create the table type to help with graphing later
				db_interface.createTable(projectname, newname, quanqual)
				print('emergency')
				return HttpResponseRedirect('/log/%s/%s/' % (projectname, newname))
		elif request.POST['formtype'] == 'edit_project':
			first = True
			edit_first = False
			edit_name = request.POST['edit_name']
			edit_description = request.POST['edit_description']
			edit_access = request.POST.getlist('acc2[]')
			edit_default_tabletype = request.POST['edit_quanqual']

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
		elif request.POST['formtype'] == "delete_project":
			db_interface.deleteProject(projectname)
			return HttpResponseRedirect('/account/')
	else:
		quanqual = db_interface.getTabletypeDefault(projectname)
		first = True
		edit_first = True

	#Check if the user has liked the project
	userp = request.user.profile
	projlist = json.decoder.JSONDecoder().decode(userp.liked_projects)
	if projectname in projlist:
		liked = True
	else:
		liked = False

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
		'lenprojectlist' : len(projectlist),
		'myproject' : myproject,
		'liked' : liked,
	}

	return render(request, "tablemanager/project_details.html", context)

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

	context = {
		"authenticated" : authenticated,
		"user" : user,
		"results" : projects,
	}
	return render(request, 'tablemanager/search.html', context)

#Ajax method
def like_project(request):
	if request.user.is_authenticated():
		popularity = 0
		if request.GET:
			if 'project' in request.GET:
				project = request.GET['project']
				userp = request.user.profile
				if userp.liked_projects == "":
					userp.liked_projects = "[]"
					userp.save()
				projlist = json.decoder.JSONDecoder().decode(userp.liked_projects)
				if project in request.user.profile.liked_projects:
					#Unlike the project
					projlist.remove(project)
					userp.liked_projects = json.dumps(projlist)
					userp.save()
					db_interface.unlikeProject(project)
				else:
					#Like the project
					projlist.append(project)
					userp.liked_projects = json.dumps(projlist)
					userp.save()
					db_interface.likeProject(project)

				projectfile = db_interface.getProject(project)
				return HttpResponse(projectfile['popularity'])
			else:
				return HttpResponseRedirect('/')
		else:
			return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect('/')

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
		return str(round(float(number)/1000000000, 1)) + "b"
	elif number > 1000000:
		return str(round(float(number)/1000000, 1)) + "m"
	elif number > 1000:
		return str(round(float(number)/1000, 1)) + "k"
	else:
		return str(number)

def getRecentProjects(userprofile):
	try:
		return json.decoder.JSONDecoder().decode(userprofile.recently_viewed_projects)
	except ValueError:
		return []

def addRecentProject(userprofile, projectname):
	#Size of your recent projects
	max_size = 5
	projlist = getRecentProjects(userprofile)
	if projectname not in projlist:
		if len(projlist) == max_size:
			projlist.pop(max_size - 1)
		projlist.insert(0, projectname)
	else:
		projlist.remove(projectname)
		projlist.insert(0, projectname)
	userprofile.recently_viewed_projects = json.dumps(projlist)
	userprofile.save()

	