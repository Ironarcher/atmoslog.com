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

#TODO: Test AJAX
#Example: atmoslog.com/api/log/12345678901234567890/exampletable/examplelog/
def log_view(request, apikey, tablename, log):
	return JsonResponse(weblog(apikey, tablename, log))

#Example: atmoslog.com/api/status/12345678901234567890/
def status_view(request, apikey):
	pass

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
	pass

