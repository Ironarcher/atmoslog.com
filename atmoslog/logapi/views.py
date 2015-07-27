from django.shortcuts import render
from django.http import *
import db_interface

# Create your views here.

def index_view(request):
	return HttpResponse("Hello. This is the web logging API")

def testview(request, apikey):
	return HttpResponse("working")

def log_view(request, apikey, tablename, log):
	if db_interface.getProjectFromKey(apikey) is None:
		return HttpResponse("failure: incorrect api key")
	else:
		project_name = db_interface.getProjectFromKey(apikey)
		if db_interface.checkTableExists(project_name, tablename) is False:
			return HttpResponse("failure: incorrect table name")
		else:
			project_name = db_interface.getProjectFromKey(apikey)

			db_interface.log(project_name, tablename, log)

			#Charge the project
			charge = db_interface.chargeProject(project_name, 1)
			if charge is None:
				return HttpResponse("Logged but failed to charge")
			else:
				#Return success
				return HttpResponse("Logged %s to Project: %s and Table: %s. %s Free logs remain." % (
					log, project_name, tablename, charge))

