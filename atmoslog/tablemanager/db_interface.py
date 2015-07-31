import random
import time
import re
from pymongo import MongoClient
import pymongo

c = MongoClient('localhost', 27017)
db = c['atmos_final']

tableBlacklist = ['projects']
maximumlength = 50

def randKey(digits):
	return ''.join(random.choice(
		'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(digits))

#Table types: qualitative, quantitative_discrete, quantitative_continuous
def createTable(ownerproject, tablename, tabletype):
	if re.match('^\w+$', tablename) is None:
		print('Only alphanumeric characters and underscores can be included in the table name.')
		return
	elif len(tablename) > maximumlength:
		print('Maximum length of the table name is 50 characters.')
		return
	elif tabletype != "qualitative" and tabletype != "quantitative_discrete" and tabletype != "quantitative_continuous":
		print('Tabletype incorrect')
		return

	projects = db['projects']
	projectfile = projects.find_one({"name" : ownerproject})
	if projectfile is not None:
		name = ownerproject + "-" + tablename
		if name not in db.collection_names():
			db.create_collection(name)
			description = {"type" : "description",
						   "tabletype" : tabletype,
						   "duplicate_loss" : 0,
						   "invalid_api_key" : 0,
						   "server_error" : 0,
						   "misc_error" : 0
						  }
			col = db[name]
			col.insert_one(description)

			tablelist = projectfile['tables']
			updatedtablelist = tablelist.append(tablename)
			#In the project description, add this table
			projects.update({'name' : 'ownerproject'}, {"$set" : {"tables" : updatedtablelist}}, upsert=False)
		else:
			print("Error: Table name in this project already exists. Choose a different name.")
	else:
		print("Error: Owner proejct does not exist")

#Access setting: Either public or private
#Status setting: running, overdrawn, stopped
def createProject(name, creator, access, description):
	if re.match('^\w+$', name) is None:
		print('Only alphanumeric characters and underscores can be included in the project name.')
		return
	elif len(name) > maximumlength:
		print('Maximum length of the project name is 50 characters.')
		return

	projects = db['projects']
	key = randKey(20)
	while(projects.find_one({"secret_key" : key})) is not None:
		key = randKey(20)

	if projects.find_one({"name" : name}) is None:
		doc = {"name" : name,
			   "description" : description,
			   "tables" : [name + '-log'],
			   "admins" : [creator],
			   "contributors" : [creator],
			   "readers" : [creator],
			   "access" : access,
			   "secret_key" : key,
			   "usd_cents" : 0.0,
			   "unpaid_logs" : 0,
			   "free_logs" : 100000,
			   "total_logs" : 0,
			   "status" : "running",
			   "popularity" : 0,
			   "default_tabletype" : "qualitative",
			   "datecreated" : int(time.time()),
			   "last_added_free_logs" : int(time.time())}
		projects.insert_one(doc)

		#Create the first table (called log)
		createTable(name, "log", "qualitative")
	else:
		print("Error: Project name already exists. Choose a different name.")

def updateProject(oldname, name, access, description, default_tabletype):
	if re.match('^\w+$', name) is None:
		print('Only alphanumeric characters and underscores can be included in the project name.')
		return
	elif len(name) > maximumlength:
		print('Maximum length of the project name is 50 characters.')
		return
	elif default_tabletype != "qualitative" and default_tabletype != "quantitative_discrete" and default_tabletype != "quantitative_continuous":
		print('Tabletype incorrect')
		return 

	projects = db['projects']
	projects.update({"name" : oldname}, {"$set" : {"name" : name, "access" : access,
		"description" : description, "default_tabletype": default_tabletype}})

	if oldname != name:
		query = db.collection_names(include_system_collections=False)
		for table in query:
			spl = table.split("-")
			if spl[0] == oldname and table not in tableBlacklist:
				newtablename = name + "-" + spl[1]
				print(table)
				db[table].rename(newtablename)

def chargeProject(project, amt):
	projects = db['projects']
	projectfile = projects.find_one({"name" : project})
	if projectfile is not None:
		free = projectfile['free_logs']
		#Take away from free logs if they still exist
		if free > 0:
			if amt >= free:
				amtToSub = free
				projects.update({"name" : project}, {"$inc":{"unpaid_logs" : amt - amtToSub}})
				return 0
			else:
				amtToSub = amt
				projects.update({"name" : project}, {"$inc":{"free_logs" : -amtToSub}})
				return free - amt
		else:
			projects.update({"name" : project}, {"$inc":{"unpaid_logs" : amt}})
			return 0
	else:
		return None

def checkProjectExists(name):
	projects = db['projects']
	if projects.find_one({"name" : name}) is None:
		#If project with that name doesn't exist, then return false.
		return False
	else:
		#Otherwise return true.
		return True

def log(project, table, value):
	name = project + "-" + table
	if db[name] is not None:
		log = {"type" : "log",
			   "value" : value,
			   "datetime" : int(time.time())}
		db[name].insert_one(log)
		projectlist = db['projects']
		projectlist.update({"name" : project}, {"$inc" : {"total_logs" : 1}})
	else:
		print('Cannot log because project or table name is not valid.')

def findlogs(project, table, amt):
	name = project + "-" + table
	coll = db[name]
	if coll is not None:
		content = []
		logs = coll.find().sort([("datecreated", pymongo.DESCENDING)]).limit(amt+1)
		print(logs)
		for post in logs:
			if post['type'] == 'log':
				content.append(post['value'])
		return content
	else:
		return '404'

def getlogcount(project, table):
	name = project + "-" + table
	coll = db[name]
	if coll is not None:
		amt = coll.count()
		#Subtract one because one is a description not a log
		return amt - 1
	else:
		return '404'

#Get all of the table names in a project
def gettables(project):
	#Get all of the collections in the database
	query = db.collection_names(include_system_collections=False)
	results = []
	for table in query:
		if table.split("-")[0] == project and table not in tableBlacklist:
			#If the table starts with the project and
			#is not in the blacklist, add it to the returned list
			results.append(table)
	return results

def checkTableExists(project, table):
	query = db.collection_names(include_system_collections=False)
	name = project + "-" + table
	if name in query:
		return True
	else:
		return False

def getProjectFromKey(apikey):
	projects = db['projects']
	projectfile = projects.find_one({"secret_key" : apikey})
	if projectfile is None:
		return None
	else:
		return projectfile['name']

def getUserProjects(username):
	projects = db['projects']
	result = []
	for project in projects.find({"admins" : username}):
		result.append(project['name'])
	return result

def getProjectAccess(project):
	projects = db['projects']
	projectfile = projects.find_one({"name" : project})
	if projectfile is None:
		return None
	else:
		return projectfile['access']

def getProject(name):
	projects = db['projects']
	projectfile = projects.find_one({"name" : name})
	return projectfile

def getTabletypeDefault(name):
	projects = db['projects']
	projectfile = projects.find_one({"name" : name})
	return projectfile['default_tabletype']

def getProjectStatus(project):
	projects = db['projects']
	projectfile = projects.find_one({"name" : project})
	return projectfile['status']

def resetKey(project):
	projects = db['projects']
	nkey = randKey(20)
	while(projects.find_one({"secret_key" : nkey})) is not None:
		nkey = randKey(20)

	projects.update({"name" : project}, {"$set" : {"secret_key" : nkey}})

def overallProjectSearch_withuser(query, username, amt):
	projects = db['projects']
	search = projects.find({"name" : {"$regex" : ".*" + query + ".*"}, "access" : "public"}).sort([("popularity", pymongo.DESCENDING)]).limit(amt)
	personal_search = projects.find({"name" : {"$regex" : ".*" + query + ".*"}, "admins" : username})

	#The search result changed to list form
	search2 = []
	#The final returned list (after compiling with private results)
	finalsearch = []
	for project in search:
		search2.append(project)

	search_names = []
	for post in search2:
		search_names.append(post['name'])

	for post in personal_search:
		if post['name'] not in search_names:
			finalsearch.append(post)

	for post in search2:
		finalsearch.append(post)

	return finalsearch

def overallProjectSearch(query, amt):
	projects = db['projects']
	search = projects.find({"name" : {"$regex" : ".*" + query + ".*"}, "access" : "public"}).sort([("popularity", pymongo.DESCENDING)]).limit(amt)
	return search

def changeStatus(projectname, status):
	projects = db['projects']
	if status == "running" or status == "stopped" or status == "overdrawn":
		projects.update({"name" : projectname}, {"$set": {"status" : status}})
