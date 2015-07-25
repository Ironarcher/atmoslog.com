import random
import time
import re
from pymongo import MongoClient

c = MongoClient('localhost', 27017)
db = c['atmos_final']

tableBlacklist = ['projects']
maximumlength = 50

def randKey(digits):
	return ''.join(random.choice(
		'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(digits))

def createTable(ownerproject, tablename):
	if re.match('^\w+$', tablename) is None:
		print('Only alphanumeric characters and underscores can be included in the table name.')
		return
	elif len(tablename) > maximumlength:
		print('Maximum length of the table name is 50 characters.')
		return

	projects = db['projects']
	projectfile = projects.find_one({"name" : ownerproject})
	if projectfile is not None:
		name = ownerproject + "-" + tablename
		if name not in db.collection_names():
			db.create_collection(name)
			description = {"type" : "description",
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
			   "paid_logs" : 0,
			   "free_logs" : 10000,
			   "datecreated" : int(time.time())}
		projects.insert_one(doc)

		#Create the first table (called log)
		createTable(name, "log")
	else:
		print("Error: Project name already exists. Choose a different name.")

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
	else:
		print('Cannot log because project or table name is not valid.')

def findlogs(project, table, amt):
	name = project + "-" + table
	coll = db[name]
	if coll is not None:
		content = []
		counter = 0
		for post in coll.find():
			if counter < amt:
				if post['type'] == 'log':
					content.append(post['value'])
					counter = counter + 1
			else:
				break
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
		if table.startswith(project) and table not in tableBlacklist:
			#If the table starts with the project and
			#is not in the blacklist, add it to the returned list
			results.append(table)
	return results
