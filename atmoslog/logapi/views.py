from django.shortcuts import render
from django.http import *
import db_interface

# Create your views here.

def log_view(request, apikey, tablename, log):
	if db_interface.checkProjectExists is False:
		return HttpResponse(single_failure.json)
	elif db_interface.checkTableExists is False:
		return HttpResponse(single_failure.json)
	project_name = db_interface.getProjectFromKey(apikey)

	db_interface.log(project_name, tablename, log)

	#Charge the project 


	#Return success
	return HttpResponse(single_success.json)

