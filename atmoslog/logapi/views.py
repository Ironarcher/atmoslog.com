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
			db_interface.log(project_name, tablename, log)

			#Charge the project
			charge = db_interface.chargeProject(project_name, 1)
			if charge is None:
				result['error'] = "Logged but failed to charge"
			else:
				#Return success
				result['error'] = ""

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

#TODO: Check status before charging
#TODO: Charge user who is calling
#TODO: Test AJAX
#Example: atmoslog.com/api/log/12345678901234567890/exampletable/examplelog/
def log_view(request, apikey, tablename, log):
	return JsonResponse(weblog(apikey, tablename, log))

#Example: atmoslog.com/api/status/12345678901234567890/
def status_view(request, apikey):
	pass

#Example: atmoslog.com/api/createtable/12345678901234567890/exampletable
def createtable_view(request, apikey, tablename):
	pass

#Example: atmoslog.com/api/bulklog/12345678901234567890/exampletable/log1&log2&log3&log4!%><&
#After splitting by '&', convert '!%><' to '&'
def bulklog_view(request, apikey, tablename, log):
	pass

