from django.shortcuts import render
from django.http import HttpResponse, Http404
import db_interface

# Create your views here.

def index(request):
	return HttpResponse("Hello, world. You're at the log manager.")

def settings(request):
	return HttpResponse("Settings")

def log(request):
	context = {}
	return render(request, 'tablemanager/log.html', context)

def projectlog(request, projectname, tablename):
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
