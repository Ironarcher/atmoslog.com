from django.shortcuts import render
from django.http import *
import db_interface

# Create your views here.

def index_view(request):
	return HttpResponse("Hello. This is the web logging API")

def testview(request, apikey):
	return HttpResponse("working")

def weblog(apikey, tablename, log):
	result = {}
	if db_interface.getProjectFromKey(apikey) is None:
		result['error'] = "incorrect api key"
	else:
		project_name = db_interface.getProjectFromKey(apikey)
		if db_interface.checkTableExists(project_name, tablename) is False:
			result['error'] = "incorrect table name"
		else:
			status = db_interface.getProjectStatus(project_name)
			if status == "overdrawn":
				result['error'] = "project overdrawn (add funds)"
			elif status == "stopped":
				result['error'] = "project stopped by user"
			elif status == 'running':
				db_interface.log(project_name, tablename, log)

				#Charge the project
				charge = db_interface.chargeProject(project_name, 1)
				if charge == "failure":
					result['error'] = "logged but failed to charge"
				else:
					#Return success
					result['error'] = ""
			else:
				result['error'] = "processing error"

	if result['error'] == "":
		result['log'] = log
		result['project_name'] = project_name
		result['table_name'] = tablename
		result['free_logs_left'] = charge
	else:
		result['log'] = ""
		result['project_name'] = ""
		result['table_name'] = ""
		result['free_logs_left'] = ""
	return result

def weblogbulk(apikey, tablename, loglist):
	result = {}
	if db_interface.getProjectFromKey(apikey) is None:
		result['error'] = "incorrect api key"
	else:
		project_name = db_interface.getProjectFromKey(apikey)
		if db_interface.checkTableExists(project_name, tablename) is False:
			result['error'] = "incorrect table name"
		else:
			status = db_interface.getProjectStatus(project_name)
			if status == "overdrawn":
				result['error'] = "project_overdrawn"
			elif status == "stopped":
				result['error'] = "project_stopped"
			elif status == 'running':
				for log in loglist:
					db_interface.log(project_name, tablename, log)

				#Charge the project
				charge = db_interface.chargeProject(project_name, len(loglist))
				if charge == "failure":
					result['error'] = "logged but failed to charge"
				else:
					#Return success
					result['error'] = ""
			else:
				result['error'] = "processing error"

	if result['error'] == "":
		result['log'] = loglist
		result['project_name'] = project_name
		result['table_name'] = tablename
		result['free_logs_left'] = charge
	else:
		result['log'] = ""
		result['project_name'] = ""
		result['table_name'] = ""
		result['free_logs_left'] = ""
	return result

#TODO: Test AJAX
#Example: atmoslog.com/api/log/12345678901234567890/exampletable/examplelog/
def log_view(request, apikey, tablename, log):
	return JsonResponse(weblog(apikey, tablename, log))

#Example: atmoslog.com/api/status/12345678901234567890/
def status_view(request, apikey):
	result = {}
	project_name = db_interface.getProjectFromKey(apikey)
	if project_name is None:
		result['error'] = "incorrect api key"
		result['project_status'] = ""
		result['server_status'] = ""
	else:
		result['error'] = ""
		project_status = db_interface.getProjectStatus(project_name)
		if project_status == "overdrawn":
			result['project_status'] = "overdrawn"
			result['server_status'] = "on"
		elif project_status == "stopped":
			result['project_status'] = "stopped"
			result['server_status'] = "on"
		elif project_status == 'running':
			result['project_status'] = "running"
			result['server_status'] = "on"
		else:
			result['error'] = "server_error"
	return JsonResponse(result)

#Example: atmoslog.com/api/createtable/12345678901234567890/exampletable
def createtable_view(request, apikey, tablename):
	result = {}
	if db_interface.getProjectFromKey(apikey) is None:
		result['error'] = "incorrect api key"
	else:
		project_name = db_interface.getProjectFromKey(apikey)
		if db_interface.checkTableExists(project_name, tablename) is True:
			result['error'] = "table name already taken"
		else:
			default_tabletype = db_interface.getTabletypeDefault(project_name)
			db_interface.createTable(project_name, tablename, default_tabletype)
			result['error'] = ""
			result['result'] = "success"
			result['project_name'] = project_name
			result['table_name'] = tablename
			result['table_type'] = default_tabletype
			return JsonResponse(result)

	#Indicates failure
	result['result'] = "failure"
	result['project_name'] = ""
	result['table_name'] = ""
	result['table_type'] = ""
	return JsonResponse(result)

#Example: atmoslog.com/api/bulklog/12345678901234567890/exampletable/log1&log2&log3&log4!%><&
#After splitting by '&', convert '!%><' to '&'
def bulklog_view(request, apikey, tablename, log):
	loglist = []
	process_log = log.split("&")
	for post in process_log:
		loglist.append(post.replace("!%><", "&"))
	return JsonResponse(weblogbulk(apikey, tablename, loglist))


